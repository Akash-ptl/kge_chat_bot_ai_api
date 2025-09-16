# app/models/app.py
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime

class AppModel(BaseModel):
    id: Optional[str] = Field(
        alias="_id",
        default=None,
        example="a1b2c3d4-e5f6-7a8b-9c0d-e1f2a3b4c5d6"
    )
    name: str = Field(..., example="Demo Chatbot App")
    description: Optional[str] = Field(None, example="A chatbot for demo purposes.")
    welcomeMessage: Dict[str, str] = Field(
        ..., example={"en": "Welcome!", "es": "¡Bienvenido!"}
    )
    acknowledgmentMessage: Dict[str, str] = Field(
        default_factory=lambda: {"en": "You're welcome!"},
        example={"en": "You're welcome!", "es": "¡De nada!"}
    )
    defaultLanguage: str = Field(..., example="en")
    availableLanguages: List[str] = Field(..., example=["en", "es"])
    googleApiKey: Optional[str] = Field(None)
    mongodbConnectionString: str = Field(
        ...,
        example="mongodb://localhost:27017/app_db_name",
        description="MongoDB connection string for this app's data storage"
    )
    createdAt: datetime = Field(default_factory=datetime.utcnow, example="2025-08-23T12:00:00Z")
    updatedAt: datetime = Field(default_factory=datetime.utcnow, example="2025-08-23T12:00:00Z")
