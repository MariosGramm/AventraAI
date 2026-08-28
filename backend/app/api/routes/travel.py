
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
PAID_TIER_LIMIT = 20

router = APIRouter(tags=["travel"])

def _check_and_update_freemium(session: SessionDep, current_user: CurrentUserDep) -> None:
    """Check freemium quota and reset if needed. Raises 429 if limit reached."""

    if current_user.is_superuser:
        return

    now = datetime.now(UTC)

    if (current_user.searches_reset_date is None or now >= current_user.searches_reset_date):
        current_user.monthly_searches_used = 0
        current_user.monthly_messages_used = 0
        current_user.searches_reset_date = now + relativedelta(months=1)
        session.add(current_user)
        session.commit()
        session.refresh(current_user)

    if current_user.subscription_tier == enums.SubscriptionTier.FREE:
        if current_user.monthly_searches_used >= FREE_TIER_LIMIT:
            raise HTTPException(429, f"Monthly itinerary limit of {FREE_TIER_LIMIT} reached. Upgrade to Pro for more searches.")
    elif current_user.subscription_tier == enums.SubscriptionTier.PAID:
        if current_user.monthly_searches_used >= PAID_TIER_LIMIT:
            raise HTTPException(429, f"Monthly itinerary limit of {PAID_TIER_LIMIT} reached. Your limit resets next month.")




@router.post("/searches", response_model=SearchSessionPublicDTO)
def create_search(session: SessionDep, current_user: CurrentUserDep, search_session_create_data: SearchSessionCreateDTO) -> Any:
    """
    Create a new search session and run the travel agent pipeline.
    Enforces freemium quota for free tier users.
    """
    _check_and_update_freemium(session, current_user)

    trip_days = (search_session_create_data.date_to - search_session_create_data.date_from).days
    if trip_days > 15:
        raise HTTPException(400, "Trip duration cannot exceed 15 days.")
    if trip_days < 1:
        raise HTTPException(400, "Trip must be at least 1 day.")

    search_session = crud.create_search_session(session=session, owner_id=current_user.id, search_session_creation_data=search_session_create_data)

    try:
        # Run agent pipeline -> Search Mode (run_search method)
        agent_pipeline = TravelAgentPipeline()
        result = agent_pipeline.run_search(search_session_create_data, current_user)

        packages_data = result.get("packages", [result]) if "packages" in result else [result]

        for pac_data in packages_data:
            itinerary_data      = pac_data.pop("itinerary", [])
            pac_data.pop("accommodations", [])

            tier_raw = pac_data.get("tier", "standard").lower()
            tier_map = {"mid": "standard", "budget": "budget", "standard": "standard", "luxury": "luxury"}
            tier = enums.TravelPackageTier(tier_map.get(tier_raw, "standard"))

            package = TravelPackage(
                session_id=search_session.id,
                tier=tier,
                estimated_cost_min=pac_data.get("estimated_cost_min"),
                estimated_cost_max=pac_data.get("estimated_cost_max"),
                currency=enums.Currency(pac_data.get("currency", "EUR").upper()),
                transportation=pac_data.get("transportation"),
                flight_info=pac_data.get("flight_info"),
                booking_info=pac_data.get("booking_info"),
                weather_summary=pac_data.get("weather_summary"),
                travel_tips=pac_data.get("travel_tips", []),
                destination_photos=pac_data.get("destination_photos", []),
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
                    activity_type_raw = activity_data.get("type", "sightseeing").lower()
                    activity_type_map = {"sightseeing": "sightseeing", "food": "food", "adventure": "adventure"}
                    activity_type = enums.ActivityType(activity_type_map.get(activity_type_raw, "sightseeing"))
                    activity = Activity(
                        itinerary_id=itinerary.id,
                        title=activity_data.get("title"),
                        type=activity_type,
                        estimated_cost=activity_data.get("estimated_cost"),
                        average_duration_hours=activity_data.get("average_duration_hours"),
                        part_of_day=enums.PartOfDay(activity_data.get("part_of_day", "morning").lower()),
                    )
                    session.add(activity)

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
        import logging
        logging.getLogger(__name__).exception("Search pipeline failed for session %s", search_session.id)
        raise HTTPException(status_code=500, detail="Something went wrong while generating your travel package. Please try again.")

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

    pdf_bytes = _build_pdf(search_session)

    from urllib.parse import quote
    safe_filename = quote(search_session.destination.replace(' ', '_'), safe='_')

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{safe_filename}_itinerary.pdf"}
    )


def _build_pdf(search_session: SearchSession) -> bytes:
    from fpdf import FPDF

    pdf = FPDF()
    import platform
    if platform.system() == 'Windows':
        pdf.add_font('Arial', fname='C:/Windows/Fonts/arial.ttf')
        pdf.add_font('ArialB', fname='C:/Windows/Fonts/arialbd.ttf')
        pdf.add_font('ArialI', fname='C:/Windows/Fonts/ariali.ttf')
    else:
        pdf.add_font('Arial', fname='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
        pdf.add_font('ArialB', fname='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
        pdf.add_font('ArialI', fname='/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf')
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # Header
    pdf.set_font("ArialB", size=20)
    pdf.set_text_color(127, 119, 221)
    pdf.cell(0, 10, "AventraAI", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Arial", size=11)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 6, f"Travel Package - {search_session.destination}", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("ArialB", size=12)
    pdf.set_text_color(83, 74, 183)
    date_from_str = f"{search_session.date_from.day:02d}/{search_session.date_from.month:02d}/{search_session.date_from.year}"
    date_to_str = f"{search_session.date_to.day:02d}/{search_session.date_to.month:02d}/{search_session.date_to.year}"
    pdf.cell(0, 7, f"{date_from_str}  -  {date_to_str}", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Arial", size=10)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 6, f"{search_session.adults} adults{f', {search_session.children} children' if search_session.children else ''}", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)
    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(6)

    packages = search_session.travel_packages or []
    for pkg in packages:
        pdf.set_font("ArialB", size=16)
        pdf.set_text_color(38, 33, 92)
        pdf.cell(0, 9, f"{search_session.destination} - {pkg.tier.value.capitalize()}", new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("Arial", size=12)
        pdf.set_text_color(83, 74, 183)
        pdf.cell(0, 7, f"Estimated cost: {int(pkg.estimated_cost_min)}-{int(pkg.estimated_cost_max)} {pkg.currency.value}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

        if pkg.weather_summary:
            pdf.set_font("ArialI", size=10)
            pdf.set_text_color(100, 100, 100)
            pdf.multi_cell(0, 5, f"Weather: {pkg.weather_summary}")
            pdf.ln(3)

        pdf.set_font("ArialB", size=13)
        pdf.set_text_color(38, 33, 92)
        pdf.cell(0, 8, "Itinerary", new_x="LMARGIN", new_y="NEXT")

        for day in sorted(pkg.itinerary, key=lambda d: d.day_number):
            pdf.set_font("ArialB", size=11)
            pdf.set_text_color(83, 74, 183)
            pdf.cell(0, 7, f"Day {day.day_number}", new_x="LMARGIN", new_y="NEXT")

            pdf.set_font("Arial", size=10)
            pdf.set_text_color(80, 80, 80)
            pdf.set_x(10)
            pdf.multi_cell(0, 5, day.description, align="L")

            for act in sorted(day.activities, key=lambda a: ['morning', 'afternoon', 'evening'].index(a.part_of_day.value)):
                pdf.set_font("Arial", size=9)
                pdf.set_text_color(60, 60, 60)
                pdf.set_x(10)
                pdf.multi_cell(0, 5, f"  {act.part_of_day.value.capitalize()}: {act.title}", align="L")
            pdf.ln(2)

        if pkg.booking_info:
            import re as _re
            booking_url = (_re.search(r'https?://\S+', pkg.booking_info) or None)
            if booking_url:
                pdf.set_font("Arial", size=10)
                pdf.set_text_color(83, 74, 183)
                pdf.cell(0, 6, "Browse available hotels", new_x="LMARGIN", new_y="NEXT", link=booking_url.group())
                pdf.ln(2)

        if pkg.transportation:
            pdf.set_font("ArialB", size=11)
            pdf.set_text_color(38, 33, 92)
            pdf.cell(0, 6, "Transportation", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Arial", size=10)
            pdf.set_text_color(80, 80, 80)
            pdf.set_x(10)
            pdf.multi_cell(0, 5, pkg.transportation, align="L")
            pdf.ln(2)

        if pkg.flight_info:
            import re as _re
            flight_url = (_re.search(r'https?://\S+', pkg.flight_info) or None)
            if flight_url:
                pdf.set_font("Arial", size=10)
                pdf.set_text_color(83, 74, 183)
                pdf.cell(0, 6, "Browse available flights", new_x="LMARGIN", new_y="NEXT", link=flight_url.group())
                pdf.ln(2)

        if pkg.travel_tips:
            pdf.set_font("ArialB", size=13)
            pdf.set_text_color(38, 33, 92)
            pdf.cell(0, 8, "Tips", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Arial", size=10)
            pdf.set_text_color(80, 80, 80)
            for tip in pkg.travel_tips:
                pdf.set_x(10)
                pdf.multi_cell(0, 5, f"  * {tip}", align="L")
            pdf.ln(3)

        pdf.set_draw_color(200, 200, 200)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(6)

    pdf.set_font("ArialI", size=8)
    pdf.set_text_color(170, 170, 170)
    pdf.cell(0, 5, "Generated by AventraAI", align="C")

    return pdf.output()









    