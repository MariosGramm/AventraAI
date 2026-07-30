
from sqlmodel import col, func, select
from app.api.deps import SessionDep
from app.models import User, UsersPublicDTO
from fastapi import APIRouter, HTTPException


router = APIRouter(tags=["users"])

@router.get("/", response_model= UsersPublicDTO)
def read_users(session:SessionDep, user: User, pagination_skip:int = 0 , pagination_limit:int = 100 ):
    """
    Method for user retrieval. Only available to superusers.
    """
    if not user.is_superuser:
        raise HTTPException(403, "User does not have sufficient rights for this action")
    elif not user.is_active:
        raise HTTPException(400, detail="User is not active")

    count_query = select(func.count()).select_from(User)
    users_count = session.exec(count_query).one()

    #Pagination
    users_query = select(User).order_by(col("created_at").desc).offset(pagination_skip).limit(pagination_limit)

    users = session.exec(users_query).all()

    usersPublicDTO = [UsersPublicDTO.model_validate(user) for user in users]

    return UsersPublicDTO(data= usersPublicDTO, count= users_count)






