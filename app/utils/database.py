# app/utils/database.py
from typing import Dict, Tuple, Any
from ..db_manager import db_manager, app_collection
import logging

logger = logging.getLogger(__name__)

async def get_app_and_collections(app_id: str) -> Tuple[Dict, Dict[str, Any]]:
    """
    Get app information and its associated database collections.

    Args:
        app_id: The app ID to look up

    Returns:
        Tuple of (app_doc, collections_dict)

    Raises:
        ValueError: If app not found
    """
    # Get app from main database
    app = await app_collection.find_one({"_id": app_id})
    if not app:
        raise ValueError(f"App not found: {app_id}")

    # Get app-specific collections
    mongodb_connection = app.get("mongodbConnectionString")
    if not mongodb_connection:
        raise ValueError(f"App {app_id} missing MongoDB connection string")

    collections = await db_manager.get_app_collections(mongodb_connection)

    return app, collections

async def get_app_collection_by_name(app_id: str, collection_name: str) -> Any:
    """
    Get a specific collection for an app.

    Args:
        app_id: The app ID
        collection_name: Name of the collection (app_content, chat_sessions, etc.)

    Returns:
        The requested collection
    """
    app, collections = await get_app_and_collections(app_id)

    if collection_name not in collections:
        raise ValueError(f"Collection '{collection_name}' not found for app {app_id}")

    return collections[collection_name]
