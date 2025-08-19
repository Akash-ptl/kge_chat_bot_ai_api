
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime

class QnAContent(BaseModel):
	question: str
	answer: str
	language: str

class NoteContent(BaseModel):
	text: str
	language: str

class URLContent(BaseModel):
	url: str
	description: Optional[str] = None
	language: str

class DocumentContent(BaseModel):
	filename: str
	filetype: str
	url: Optional[str] = None
	language: str

class AppContentModel(BaseModel):
	id: Optional[str] = Field(alias="_id", default=None)
	appId: str
	contentType: Literal["qa", "note", "url", "document"]
	content: dict
	embedding: Optional[List[float]] = None
	sourceRef: Optional[str] = None
	createdAt: Optional[datetime] = Field(default_factory=datetime.utcnow)
	updatedAt: Optional[datetime] = Field(default_factory=datetime.utcnow)
