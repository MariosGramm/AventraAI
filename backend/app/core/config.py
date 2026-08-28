from pathlib import Path
import secrets
from typing import Annotated, Literal, Self
import warnings
from dotenv import load_dotenv
from pydantic import AnyUrl, BeforeValidator, EmailStr, HttpUrl, PostgresDsn, computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
ENV_FILE = BASE_DIR / ".env"
load_dotenv(ENV_FILE, override=False)

def parse_cors_origins(origins: str) -> list[str] | str:
    """
    Parse a string of CORS origins into a list.

    Args:
        origins (str): A string of CORS origins, separated by commas.

    Returns:
        list: A list of CORS origins.
    """
    if isinstance(origins, list):
        return origins
    if origins.startswith("[") and origins.endswith("]"):
        return [origin.strip() for origin in origins[1:-1].split(",")]
    return [origin.strip() for origin in origins.split(",")]

class Settings(BaseSettings):
    """
    Settings class for application configuration.

    Properties / Attributes:
        model_config (SettingsConfigDict): Configuration for the settings model.
        API_V1_STR (str): The base URL for the API version 1.
        SECRET_KEY (str): A secret key for cryptographic operations.
        ACCESS_TOKEN_EXPIRE_MINUTES (int): The expiration time for access tokens in minutes.
        FRONTEND_HOST (str): The host URL for the frontend application.
        ENVIRONMENT (Literal): The environment in which the application is running.
        BACKEND_CORS_ORIGINS (list[AnyUrl] | str): A list of allowed CORS origins for the backend.
        PROJECT_NAME (str): The name of the project.
        SENTRY_DSN (HttpUrl | None): The DSN for Sentry error tracking.
        POSTGRES_SERVER (str): The server address for the PostgreSQL database.
        POSTGRES_PORT (int): The port number for the PostgreSQL database.
        POSTGRES_USER (str): The username for the PostgreSQL database.
        POSTGRES_PASSWORD (str): The password for the PostgreSQL database.
        POSTGRES_DB (str): The name of the PostgreSQL database.
        SMTP_TLS (bool): Whether to use TLS for SMTP connections.
        SMTP_SSL (bool): Whether to use SSL for SMTP connections.
        SMTP_PORT (int): The port number for the SMTP server.
        SMTP_HOST (str | None): The host address for the SMTP server.
        SMTP_USER (str | None): The username for the SMTP server.
        SMTP_PASSWORD (str | None): The password for the SMTP server.
        EMAILS_FROM_EMAIL (EmailStr | None): The email address from which emails are sent.
        EMAILS_FROM_NAME (str | None): The name from which emails are sent.
        EMAIL_RESET_TOKEN_EXPIRE_HOURS (int): The expiration time for email reset tokens in hours.
        RESEND_API_KEY (str): API key of email provider.
        GOOGLE_CLIENT_ID (str): Identifies the application to Google.  
        GOOGLE_CLIENT_SECRET (str): A secret associated with the application, used to authenticate the application to Google.
        SENTRY_DSN (HttpUrl | None): The DSN for Sentry error tracking.
        STRIPE_PRICE_ID: The unique ID of a specific product price in Stripe. It tells Stripe which price/plan the customer should be charged for.
        STRIPE_SECRET_KEY: A private API key used to securely connect your application to Stripe and perform actions such as creating payments or managing customers.
    """
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )

    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # JWT token expires after 24 hours
    FRONTEND_HOST: str = "http://localhost:5173"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors_origins)
    ] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
            self.FRONTEND_HOST
        ]
    
    PROJECT_NAME: str = "AventraAI"
    SENTRY_DSN: HttpUrl | None = None
    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """
        Constuct the SQLAlchemy database URI for connecting to the PostgreSQL database.
        """
        return str(PostgresDsn.build(
            scheme = "postgresql+psycopg",
            username = self.POSTGRES_USER,
            password = self.POSTGRES_PASSWORD,
            host = self.POSTGRES_SERVER,
            port = self.POSTGRES_PORT,
            path = self.POSTGRES_DB
        ))

    # Google
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    # Stripe
    STRIPE_PRICE_ID: str = ""
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: EmailStr | None = None
    EMAILS_FROM_NAME: str | None = None
    RESEND_API_KEY: str = ""

    @model_validator(mode="after")
    def _set_default_emails_from(self) -> Self:
        if not self.EMAILS_FROM_NAME:
            self.EMAILS_FROM_NAME = self.PROJECT_NAME
        return self
    
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48

    @computed_field  # type: ignore[prop-decorator]
    @property
    def emails_enabled(self) -> bool:
        return bool(self.RESEND_API_KEY and self.EMAILS_FROM_EMAIL)
    
    EMAIL_TEST_USER: EmailStr = "test@example.com"
    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_PASSWORD: str
    
    def _check_default_secret(self:object , var_name:str, var_value:str | None) -> None:
        """
        Check if the default secret value is "changethis" and raise a ValueError if it is.
        """
        if var_value == "changethis":
            message = (
                f"WARNING: The {var_name} is set to the default value 'changethis'. "
                "Please change it to a secure value in your .env file."
            )
            if self.ENVIRONMENT == "local":
                warnings.warn(message, stacklevel=1)
            else:
                raise ValueError(message)
            
    @model_validator(mode="after")
    def _enforce_non_default_secrets(self: Self) -> Self:
        """
        Enforce that certain secret values are not set to their default values.
        """
        self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
        self._check_default_secret("POSTGRES_PASSWORD", self.POSTGRES_PASSWORD)
        self._check_default_secret("FIRST_SUPERUSER_PASSWORD", self.FIRST_SUPERUSER_PASSWORD)

        return self
    
settings = Settings() # type: ignore



    