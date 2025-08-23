# app/db.py
from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings

client = AsyncIOMotorClient(settings.MONGO_URL)
db = client[settings.MONGO_DB_NAME]

# Collections


# Exported collections for use in routers
app_collection = db["apps"]
app_content_collection = db["app_content"]
app_guardrails_collection = db["app_guardrails"]
chat_sessions_collection = db["chat_sessions"]
chat_messages_collection = db["chat_messages"]

# Aliases for backward compatibility with routers (must be after originals)
apps_collection = app_collection
guardrails_collection = app_guardrails_collection
