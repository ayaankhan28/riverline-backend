from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Backend"
    API_V1_STR: str = "/api/v1"
    
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "app"
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    LIVEKIT_URL: str = os.getenv("LIVEKIT_URL")
    LIVEKIT_API_KEY: str = os.getenv("LIVEKIT_API_KEY")
    LIVEKIT_API_SECRET: str = os.getenv("LIVEKIT_API_SECRET")
    LIVEKIT_TRUNK_ID: str = os.getenv("LIVEKIT_TRUNK_ID")
    # Twilio Configuration

    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER: str = os.getenv("TWILIO_PHONE_NUMBER")

    # SIP Configuration
    TRUNK_USERNAME: str = os.getenv("TRUNK_USERNAME")
    TRUNK_PASSWORD: str = os.getenv("TRUNK_PASSWORD")
    TRUNK_HOST: str = os.getenv("TRUNK_HOST")

    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    CARTESIA_API_KEY: str = os.getenv("CARTESIA_API_KEY")

    @property
    def get_database_url(self) -> str:
        if self.SQLALCHEMY_DATABASE_URI:
            return self.SQLALCHEMY_DATABASE_URI
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 