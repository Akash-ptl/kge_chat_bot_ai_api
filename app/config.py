# app/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGO_URL: str
    MONGO_DB_NAME: str = "ai_chat_bot"
    GOOGLE_API_KEY: str = ""


    class Config:
        env_file = ".env"

settings = Settings()
