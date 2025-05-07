from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class Settings(BaseSettings):
    DATABASE_URL: str
    GEMINI_API_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()

