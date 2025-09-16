# app/db_manager.py
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Dict, Optional, Any
import logging
from urllib.parse import urlparse
from .config import settings

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Manages multiple MongoDB connections for multi-tenant architecture.
    Each app has its own database connection.
    """

    def __init__(self):
        # Main database connection for app metadata
        self.main_client = AsyncIOMotorClient(settings.MONGO_URL)
        self.main_db = self.main_client[settings.MONGO_DB_NAME]

        # Cache of app-specific database connections
        self._app_clients: Dict[str, AsyncIOMotorClient] = {}
        self._app_dbs: Dict[str, Any] = {}

    def get_main_db(self):
        """Get the main database for app metadata storage."""
        return self.main_db

    async def get_app_db(self, mongodb_connection_string: str) -> Any:
        """
        Get or create a database connection for a specific app.

        Args:
            mongodb_connection_string: MongoDB connection string for the app

        Returns:
            Database instance for the app
        """
        # Use connection string as cache key
        cache_key = mongodb_connection_string

        if cache_key in self._app_dbs:
            return self._app_dbs[cache_key]

        try:
            # Parse the connection string to extract database name
            parsed = urlparse(mongodb_connection_string)
            db_name = parsed.path.lstrip('/') if parsed.path else 'app_data'

            # Create new client connection
            client = AsyncIOMotorClient(mongodb_connection_string)
            db = client[db_name]

            # Cache the connections
            self._app_clients[cache_key] = client
            self._app_dbs[cache_key] = db

            logger.info(f"Created new database connection for app: {db_name}")
            return db

        except Exception as e:
            logger.error(f"Failed to create database connection: {e}")
            raise

    async def get_app_collections(self, mongodb_connection_string: str) -> Dict[str, Any]:
        """
        Get all collections for a specific app database.

        Returns:
            Dictionary containing all app-specific collections
        """
        db = await self.get_app_db(mongodb_connection_string)

        return {
            'app_content': db['app_content'],
            'app_guardrails': db['app_guardrails'],
            'chat_sessions': db['chat_sessions'],
            'chat_messages': db['chat_messages']
        }

    async def close_app_connection(self, mongodb_connection_string: str):
        """Close a specific app's database connection."""
        cache_key = mongodb_connection_string

        if cache_key in self._app_clients:
            client = self._app_clients[cache_key]
            client.close()
            del self._app_clients[cache_key]
            del self._app_dbs[cache_key]
            logger.info(f"Closed database connection for: {cache_key}")

    async def close_all_connections(self):
        """Close all database connections."""
        # Close main connection
        self.main_client.close()

        # Close all app connections
        for client in self._app_clients.values():
            client.close()

        self._app_clients.clear()
        self._app_dbs.clear()
        logger.info("Closed all database connections")

# Global database manager instance
db_manager = DatabaseManager()

# Main database collections (for app metadata)
app_collection = db_manager.get_main_db()["apps"]

# Backward compatibility aliases
apps_collection = app_collection

# Legacy collections for existing code that doesn't use app-specific DBs yet
# These will be replaced as we migrate endpoints
app_content_collection = db_manager.get_main_db()["app_content"]
app_guardrails_collection = db_manager.get_main_db()["app_guardrails"]
chat_sessions_collection = db_manager.get_main_db()["chat_sessions"]
chat_messages_collection = db_manager.get_main_db()["chat_messages"]
guardrails_collection = app_guardrails_collection
