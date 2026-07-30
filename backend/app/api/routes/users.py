
from typing import Any
import uuid

from app import crud
from app.core.security import get_password_hash, verify_password
from app.utils import generate_new_account_email, send_email
from sqlmodel import col, func, select
from app.api.deps import CurrentUserDep, SessionDep, get_current_active_superuser
from app.models import Message, UpdatePassword, User, UserCreateDTO, UserCreateSignupDTO, UserPublicDTO, UserUpdateDTO, UserUpdateSelfDTO, UsersPublicDTO
from fastapi import APIRouter, Depends, HTTPException
from app.core.config import settings


router = APIRouter(tags=["users"])

@router.get("/", response_model= UsersPublicDTO, dependencies=[Depends(get_current_active_superuser)])
def read_users(session:SessionDep, pagination_skip:int = 0 , pagination_limit:int = 100 ) -> Any:
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
def create_user(session: SessionDep, user_create_data: UserCreateDTO) -> Any:
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
def update_user_me(session:SessionDep, user_update_data: UserUpdateSelfDTO, current_user: CurrentUserDep) -> Any:
    """
    Method for a user updating their own profile.
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

@router.patch("me/password", response_model= Message)
def update_password_me(*, session:SessionDep, data:UpdatePassword, current_user:CurrentUserDep) -> Any:
    """
    Method for a user updating their own password.
    """
    #Check if current password is valid
    validated , _ = verify_password( data.current_password, current_user.hashed_password)

    if not validated:
        raise HTTPException(400, "Incorrect password")

    if data.current_password == data.new_password:
        raise HTTPException(400, "New password cannot be the same as the current one")

    new_hashed_password = get_password_hash(data.new_password)
    current_user.hashed_password = new_hashed_password
    session.add(current_user)
    session.commit()

    return Message("Password updated successfully!")

@router.get("/me", response_model=UserPublicDTO)
def read_user_me(current_user:CurrentUserDep) -> Any:
    """
    Method for a user viewing their own profile.
    """
    return current_user

@router.post("/me", response_model=Message)
def delete_user_me(session:SessionDep, current_user:CurrentUserDep)-> Any :
    """
    Method for a user deleting their own profile.
    Available only to regular users. 
    """
    if current_user.is_superuser:
        raise HTTPException(403, "Superusers are not allowed to delete themselves")

    session.delete(current_user)
    session.commit()

    return Message("User deleted successfully!")     

@router.post("/signup", response_model=UserPublicDTO)
def register_user(session:SessionDep, user_register_data:UserCreateSignupDTO) -> Any :
    """
    Method for user signup.
    """
    user = crud.get_user_by_email(user_register_data.email)

    if user:
        raise HTTPException(400, "User with this email already exists")

    userCreateSignupDTO = UserCreateSignupDTO.model_validate(user_register_data)
    user_registed = crud.create_user(session, userCreateSignupDTO)

    return user_registed

@router.get("/{user_id}", response_model=UserPublicDTO)
def read_user_by_id(
    session: SessionDep,
    user_id: uuid.UUID,
    current_user: CurrentUserDep
) -> Any:
    """
    Get a specific user by ID.
    Regular users can only view themselves.
    Superusers can view any user.
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")

    #Regular users can only view themselves.
    if user == current_user:
        return user

    if not current_user.is_superuser:
        raise HTTPException(403, "User does not have enough privileges")

    #Superusers can view any user.
    return user

@router.patch("/{user_id}", response_model=UserPublicDTO, dependencies=[Depends(get_current_active_superuser)])
def update_user(session: SessionDep, user_update_data:UserUpdateDTO, user_id:uuid.UUID) -> Any :
    """
    Method for updating users.
    Available only to superusers.
    """
    user = session.get(User, user_id)

    if not user:
        raise HTTPException(404, "User with this email does not exist")

    if user_update_data.email:
        existing_user = crud.get_user_by_email(session=session, email=user_update_data.email)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )

    user = crud.update_user(session=session, db_user=user, user_in=user_update_data)
    return user

@router.delete("/{user_id}", response_model= Message, dependencies=[Depends(get_current_active_superuser)])
def delete_user(session:SessionDep, user_id:uuid.UUID, current_user:CurrentUserDep) -> Any:

    user = session.get(User, user_id)

    if not user:
        raise HTTPException(404, "User not found.")

    if user == current_user:
        raise HTTPException(403, "Superusers are not allowed to delete themselves.")

    session.delete(user)
    session.commit()
    return Message(message="User deleted successfully!")







