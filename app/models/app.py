# app/models/app.py
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime

class AppModel(BaseModel):
    id: Optional[str] = Field(alias="_id")
    name: str
    description: Optional[str]
    welcomeMessage: Dict[str, str]
    defaultLanguage: str
    availableLanguages: List[str]
    googleApiKey: str  # should be encrypted in production
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
