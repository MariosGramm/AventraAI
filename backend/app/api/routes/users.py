
from app import crud
from app.utils import generate_new_account_email, send_email
from sqlmodel import col, func, select
from app.api.deps import SessionDep, get_current_active_superuser
from app.models import User, UserCreateDTO, UserPublicDTO, UserUpdateSelfDTO, UsersPublicDTO
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
def create_user(session: SessionDep, user_create_data: UserCreateDTO):
    """
    Method for user creation. Only available to superusers.
    """
    #Check if user already exists
    user = crud.get_user_by_email(session, user_create_data.email)

    if user:
        raise HTTPException(400, "User with this email already exists")

    user_created = crud.create_user(session=session, user_creation_data=user_create_data)

    #Send welcome email
    if settings.emails_enabled:
        email_data = generate_new_account_email(
            email_to= user_created.email,
            username= user_created.email,
            password= user_create_data.password
        )

        send_email(
            email_to= user_create_data.email,
            subject= email_data.subject,
            html_content= email_data.html_content
        )

    return user_created


@router.post("/update/me", response_model=UserPublicDTO)
def update_user_me(session:SessionDep, user_update_data: UserUpdateSelfDTO, current_user: User):
    """
    Method for a user updating his own profile.
    """
    if user_update_data.email:
        existing_user = crud.get_user_by_email(session, user_update_data.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(400, "User with this email already exists")

    user_update_data_clean = user_update_data.model_dump(exclude_unset=True)
    current_user.sqlmodel_update(user_update_data_clean)

    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    return current_user                  






# TODO
# update_password_me
# read_user_me
# delete_user_me
# register_user
# read_user_by_id
# update_user
# delete_user





