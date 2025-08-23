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
    defaultLanguage: str = Field(..., example="en")
    availableLanguages: List[str] = Field(..., example=["en", "es"])
    googleApiKey: str = Field(..., example="AIzaSyDVm1IWybAQwb-AtcxwXWd3R5Oww4ZhOkc")
    createdAt: datetime = Field(default_factory=datetime.utcnow, example="2025-08-23T12:00:00Z")
    updatedAt: datetime = Field(default_factory=datetime.utcnow, example="2025-08-23T12:00:00Z")
