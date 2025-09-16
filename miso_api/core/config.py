from pydantic_settings import BaseSettings
import secrets

class Settings(BaseSettings):
    # Generate a secure secret key if not set in environment
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()
