# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # MONGO_URL: str = "mongodb://localhost:27017"
    MONGO_URL: str = "MONGO_URL: str = "mongodb+srv://akashkalathiya46_db_user:rcJpdVQsxaUUzbCQ@aichatbot.7qy2mj9.mongodb.net/ai_chat_bot""

    MONGO_DB_NAME: str = "ai_chat_bot"

    class Config:
        env_file = ".env"

settings = Settings()
