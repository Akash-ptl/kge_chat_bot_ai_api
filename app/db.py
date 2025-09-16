# app/db.py
# Import from the new database manager
from .db_manager import (
    db_manager,
    app_collection,
    apps_collection,
    app_content_collection,
    app_guardrails_collection,
    chat_sessions_collection,
    chat_messages_collection,
    guardrails_collection
)

# Keep this file for backward compatibility
# All new code should use db_manager directly for app-specific databases
