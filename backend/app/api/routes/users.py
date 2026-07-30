
from app import crud
from app.utils import generate_new_account_email, send_email
from sqlmodel import col, func, select
from app.api.deps import SessionDep, get_current_active_superuser
from app.models import User, UserCreateDTO, UserPublicDTO, UsersPublicDTO
from fastapi import APIRouter, Depends, HTTPException
from app.core.config import settings


router = APIRouter(tags=["users"])

@router.get("/", response_model= UsersPublicDTO, dependencies=[Depends(get_current_active_superuser)])
def read_users(session:SessionDep, pagination_skip:int = 0 , pagination_limit:int = 100 ):
    """
    Method for user retrieval. Only available to superusers.
    """
    count_query = select(func.count()).select_from(User)
    users_count = session.exec(count_query).one()

    #Pagination
    users_query = select(User).order_by(col("created_at").desc()).offset(pagination_skip).limit(pagination_limit)

    users = session.exec(users_query).all()

    usersPublicDTO = [UsersPublicDTO.model_validate(user) for user in users]

    return UsersPublicDTO(data= usersPublicDTO, count= users_count)

@router.post("/create", response_model= UserPublicDTO, dependencies= [Depends(get_current_active_superuser)])
def create_user(session: SessionDep, user_to_create: UserCreateDTO):
    """
    Method for user creation. Only available to superusers.
    """
    #Check if user already exists
    user = crud.get_user_by_email(session, user_to_create.email)

    if user:
        raise HTTPException(400, "User with this email already exists")

    user_created = crud.create_user(session=session, user_creation_data=user_to_create)

    #Send welcome email
    if settings.emails_enabled:
        email_data = generate_new_account_email(
            email_to= user_created.email,
            username= user_created.email,
            password= user_to_create.password
        )

        send_email(
            email_to= user_to_create.email,
            subject= email_data.subject,
            html_content= email_data.html_content
        )

    return user_created


    






