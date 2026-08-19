
from datetime import UTC, datetime

from app import enums
from typing import Any
import uuid
from app import crud
from app.agent.agent_pipeline import TravelAgentPipeline
from fastapi import APIRouter, HTTPException
from app.models import Accommodation, Activity, Itinerary, SearchSession, SearchSessionCreateDTO, SearchSessionPublicDTO, SearchSessionsPublicDTO, TravelPackage
from app.api.deps import CurrentUserDep, SessionDep
from dateutil.relativedelta import relativedelta
from sqlmodel import col, select
from sqlalchemy.orm import selectinload


FREE_TIER_LIMIT = 3

router = APIRouter(tags=["travel"])

def _check_and_update_freemium(session: SessionDep, current_user: CurrentUserDep) -> None:
    """Check freemium quota and reset if needed. Raises 429 if limit reached."""

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









    