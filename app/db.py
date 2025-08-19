# app/db.py
from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings

client = AsyncIOMotorClient(settings.MONGO_URL)
db = client[settings.MONGO_DB_NAME]

# Collections
apps_collection = db["apps"]
app_content_collection = db["app_content"]
guardrails_collection = db["app_guardrails"]
sessions_collection = db["chat_sessions"]
messages_collection = db["chat_messages"]
