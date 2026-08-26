
from datetime import UTC, datetime
import json
import io

from app import enums
from typing import Any
import uuid
from app import crud
from app.agent.agent_pipeline import TravelAgentPipeline
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.models import Accommodation, Activity, Itinerary, SearchSession, SearchSessionCreateDTO, SearchSessionPublicDTO, SearchSessionsPublicDTO, TravelPackage
from app.api.deps import CurrentUserDep, SessionDep
from dateutil.relativedelta import relativedelta
from sqlmodel import col, select
from sqlalchemy.orm import selectinload


FREE_TIER_LIMIT = 3

router = APIRouter(tags=["travel"])

def _check_and_update_freemium(session: SessionDep, current_user: CurrentUserDep) -> None:
    """Check freemium quota and reset if needed. Raises 429 if limit reached."""

    # Superusers → unlimited searches
    if current_user.is_superuser:
        return
    
    if current_user.subscription_tier != enums.SubscriptionTier.FREE:
        return # user has paid subscription , do nothing

    now = datetime.now(UTC)

    if (current_user.searches_reset_date is None or now >= current_user.searches_reset_date):
        current_user.monthly_searches_used = 0
        current_user.searches_reset_date = now + relativedelta(months=1)
        session.add(current_user)
        session.commit()
        session.refresh(current_user)

    if current_user.monthly_searches_used >= FREE_TIER_LIMIT:
        raise HTTPException(429, f"Monthly search limit of {FREE_TIER_LIMIT} reached. Upgrade to paid tier for unlimited searches.")




@router.post("/searches", response_model=SearchSessionPublicDTO)
def create_search(session: SessionDep, current_user: CurrentUserDep, search_session_create_data: SearchSessionCreateDTO) -> Any:
    """
    Create a new search session and run the travel agent pipeline.
    Enforces freemium quota for free tier users.
    """
    _check_and_update_freemium(session, current_user)

    search_session = crud.create_search_session(session=session, owner_id=current_user.id, search_session_creation_data=search_session_create_data)

    try:
        # Run agent pipeline -> Search Mode (run_search method)
        agent_pipeline = TravelAgentPipeline()
        result = agent_pipeline.run_search(search_session_create_data, current_user)

        packages_data = result.get("packages", [result]) if "packages" in result else [result]

        for pac_data in packages_data:
            itinerary_data      = pac_data.pop("itinerary", [])
            accommodations_data = pac_data.pop("accommodations", [])

            package = TravelPackage(
                session_id=search_session.id,
                tier=enums.TravelPackageTier(pac_data.get("tier", "standard").lower()),
                estimated_cost_min=pac_data.get("estimated_cost_min"),
                estimated_cost_max=pac_data.get("estimated_cost_max"),
                currency=enums.Currency(pac_data.get("currency", "EUR").upper()),
                transportation=pac_data.get("transportation"),
                flight_info=pac_data.get("flight_info"),
                weather_summary=pac_data.get("weather_summary"),
                travel_tips=pac_data.get("travel_tips", []),
            )
            session.add(package)
            session.flush()

            for day_data in itinerary_data:
                activities_data = day_data.pop("activities", [])
                itinerary = Itinerary(
                    travel_package_id=package.id,
                    day_number=day_data.get("day_number"),
                    description=day_data.get("description"),
                    estimated_daily_cost=day_data.get("estimated_daily_cost"),
                )
                session.add(itinerary)
                session.flush()

                for activity_data in activities_data:
                    activity = Activity(
                        itinerary_id=itinerary.id,
                        title=activity_data.get("title"),
                        type=enums.ActivityType(activity_data.get("type", "sightseeing").lower()),
                        estimated_cost=activity_data.get("estimated_cost"),
                        average_duration_hours=activity_data.get("average_duration_hours"),
                        part_of_day=enums.PartOfDay(activity_data.get("part_of_day", "morning").lower()),
                    )
                    session.add(activity)

            for acc_data in accommodations_data:
                accommodation = Accommodation(
                    package_id=package.id,
                    name=acc_data.get("name"),
                    type=enums.AccommodationType(acc_data.get("type", "hotel").lower()),
                    area=acc_data.get("area"),
                    cost_per_night=acc_data.get("cost_per_night"),
                    rating=acc_data.get("rating"),
                )
                session.add(accommodation)

        search_session.status = enums.SearchSessionStatus.COMPLETED
        session.add(search_session)

        current_user.monthly_searches_used += 1
        session.add(current_user)

        session.commit()

        search_session = session.exec(
            select(SearchSession)
            .where(SearchSession.id == search_session.id)
            .options(
                selectinload(SearchSession.travel_packages)
            )
        ).first()

    except Exception as e:
        session.rollback()
        search_session.status = enums.SearchSessionStatus.FAILED
        search_session.error_message = str(e)
        session.add(search_session)
        session.commit()
        raise HTTPException(status_code=500, detail=f"Agent pipeline failed: {str(e)}")

    return search_session

@router.get("/searches", response_model=SearchSessionsPublicDTO)
def get_searches(session:SessionDep, current_user:CurrentUserDep) -> Any:
    """
    Get all search sessions for the current user, ordered by most recent.
    """
    search_sessions = session.exec(
        select(SearchSession)
        .where(SearchSession.owner_id == current_user.id)
        .order_by(col(SearchSession.created_at).desc())
    ).all()

    return SearchSessionsPublicDTO(data=search_sessions, count=len(search_sessions))

@router.get("/searches/{search_session_id}", response_model=SearchSessionPublicDTO)
def get_search(
    session: SessionDep,
    search_session_id: uuid.UUID,
    current_user: CurrentUserDep
    ) -> Any:
    """
    Get a specific search session by ID including its travel packages.
    Only accessible by the session owner.
    """
    search_session = session.get(SearchSession, search_session_id)

    if not search_session:
        raise HTTPException(status_code=404, detail="Search session not found")

    if search_session.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough privileges")

    return search_session


@router.get("/searches/{search_session_id}/pdf")
def download_search_pdf(
    session: SessionDep,
    search_session_id: uuid.UUID,
    current_user: CurrentUserDep,
) -> StreamingResponse:
    """Generate and download a PDF for a search session's travel packages."""
    search_session = session.exec(
        select(SearchSession)
        .where(SearchSession.id == search_session_id)
        .options(selectinload(SearchSession.travel_packages))
    ).first()

    if not search_session:
        raise HTTPException(404, "Search session not found")
    if search_session.owner_id != current_user.id:
        raise HTTPException(403, "Not enough privileges")

    html = _build_pdf_html(search_session)

    from weasyprint import HTML
    pdf_bytes = HTML(string=html).write_pdf()

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={search_session.destination.replace(' ', '_')}_itinerary.pdf"}
    )


def _build_pdf_html(search_session: SearchSession) -> str:
    packages = search_session.travel_packages or []
    sections = []

    for pkg in packages:
        days_html = ""
        for day in sorted(pkg.itinerary, key=lambda d: d.day_number):
            activities_html = "".join(
                f"<li><strong>{a.part_of_day.capitalize()}</strong>: {a.title}"
                f"{f' ({a.estimated_cost} {pkg.currency.value})' if a.estimated_cost else ''}</li>"
                for a in sorted(day.activities, key=lambda a: ['morning', 'afternoon', 'evening'].index(a.part_of_day.value))
            )
            days_html += f"""
            <div style="margin-bottom:12px;padding-left:12px;border-left:3px solid #d4d0f8">
                <h3 style="color:#534AB7;margin:0 0 4px">Day {day.day_number}</h3>
                <p style="color:#666;margin:0 0 4px">{day.description}</p>
                <ul style="margin:0;padding-left:18px">{activities_html}</ul>
            </div>"""

        accom_html = ""
        for acc in pkg.accommodations:
            accom_html += f"<li>{acc.name} ({acc.type.value}){f', {acc.area}' if acc.area else ''}{f' — {acc.cost_per_night} {pkg.currency.value}/night' if acc.cost_per_night else ''}{f' ★ {acc.rating}' if acc.rating else ''}</li>"

        tips_html = "".join(f"<li>{t}</li>" for t in (pkg.travel_tips or []))

        sections.append(f"""
        <div style="margin-bottom:24px">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
                <h2 style="margin:0;color:#26215C">{search_session.destination} — {pkg.tier.value.capitalize()}</h2>
                <span style="color:#534AB7;font-size:18px;font-weight:600">{pkg.estimated_cost_min}–{pkg.estimated_cost_max} {pkg.currency.value}</span>
            </div>
            {f'<p style="background:#f8f8ff;padding:8px 12px;border-radius:8px;color:#534AB7">☀ {pkg.weather_summary}</p>' if pkg.weather_summary else ''}
            <h3 style="color:#26215C">Itinerary</h3>
            {days_html}
            {f'<h3 style="color:#26215C">Accommodation</h3><ul>{accom_html}</ul>' if accom_html else ''}
            {f'<p><strong>Transportation:</strong> {pkg.transportation}</p>' if pkg.transportation else ''}
            {f'<p>{pkg.flight_info}</p>' if pkg.flight_info else ''}
            {f'<h3 style="color:#26215C">Tips</h3><ul>{tips_html}</ul>' if tips_html else ''}
        </div>
        """)

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
    body {{ font-family: 'Helvetica Neue', Arial, sans-serif; color: #26215C; padding: 32px; font-size: 13px; line-height: 1.6; }}
    h2 {{ font-size: 20px; }} h3 {{ font-size: 14px; margin: 12px 0 6px; }}
    hr {{ border: none; border-top: 1px solid #e8e6f0; margin: 24px 0; }}
</style>
</head><body>
<div style="text-align:center;margin-bottom:24px">
    <h1 style="color:#7F77DD;font-size:24px;margin:0">AventraAI</h1>
    <p style="color:#aaa;margin:4px 0">Travel Package — {search_session.destination}</p>
    <p style="color:#aaa;font-size:12px">{search_session.date_from.strftime('%b %d, %Y')} → {search_session.date_to.strftime('%b %d, %Y')} · {search_session.adults} adults{f', {search_session.children} children' if search_session.children else ''}</p>
</div>
<hr>
{'<hr>'.join(sections)}
<div style="text-align:center;color:#aaa;font-size:11px;margin-top:32px">Generated by AventraAI · aventraai.com</div>
</body></html>"""









    