from sqlmodel import Session, create_engine, select

from app import crud
from app.core.config import settings
from app.models import User, UserCreateDTO

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)

def init_db(session: Session) -> None:
    """
    Initialize the database with default data.
    Fetches the first superuser from the database using the email specified in the settings. 
    If the superuser does not exist, it creates a new superuser with the provided email and password.
    """

    user = session.exec(select (User).where(User.email == settings.FIRST_SUPERUSER)).first()

    if not user: 
        first_superuser = UserCreateDTO(
            email = settings.FIRST_SUPERUSER,
            password = settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser = True
        )

        user = crud.user.create(session, user_create = first_superuser)

