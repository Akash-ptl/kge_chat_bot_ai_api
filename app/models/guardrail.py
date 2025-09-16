from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime

class GuardrailModel(BaseModel):
	id: Optional[str] = Field(alias="_id", default=None)
	app_id: str
	ruleName: str
	ruleType: str
	pattern: str
	action: str
	responseMessage: Dict[str, str]
	isActive: bool = True
	createdAt: Optional[datetime] = Field(default_factory=datetime.utcnow)
	updatedAt: Optional[datetime] = Field(default_factory=datetime.utcnow)

	class Config:
		json_schema_extra = {
			"example": {
				"_id": "b7e6c2e2-8c2e-4b7e-9c2e-8c2e4b7e9c2e",
				"app_id": "a1b2c3d4-e5f6-7a8b-9c0d-e1f2a3b4c5d6",
				"ruleName": "Block offensive language",
				"ruleType": "blacklist_phrase",
				"pattern": "badword",
				"action": "block",
				"responseMessage": {"en": "Your message was blocked.", "es": "Su mensaje fue bloqueado."},
				"isActive": True,
				"createdAt": "2025-08-23T12:00:00Z",
				"updatedAt": "2025-08-23T12:00:00Z"
			}
		}
