from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime

class GuardrailModel(BaseModel):
	id: Optional[str] = Field(alias="_id", default=None)
	appId: str
	ruleName: str
	ruleType: str
	pattern: str
	action: str
	responseMessage: Dict[str, str]
	isActive: bool = True
	createdAt: Optional[datetime] = Field(default_factory=datetime.utcnow)
	updatedAt: Optional[datetime] = Field(default_factory=datetime.utcnow)
