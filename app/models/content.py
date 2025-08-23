
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime

class QnAContent(BaseModel):
	question: str
	answer: str
	language: str

	class Config:
		schema_extra = {
			"example": {
				"question": "What is FastAPI?",
				"answer": "FastAPI is a modern, fast web framework for building APIs with Python.",
				"language": "en"
			}
		}

class NoteContent(BaseModel):
	text: str
	language: str

	class Config:
		schema_extra = {
			"example": {
				"text": "This is a note about the chatbot system.",
				"language": "en"
			}
		}

class URLContent(BaseModel):
	url: str
	description: Optional[str] = None
	language: str

	class Config:
		schema_extra = {
			"example": {
				"url": "https://fastapi.tiangolo.com/",
				"description": "Official FastAPI documentation",
				"language": "en"
			}
		}

class DocumentContent(BaseModel):
	filename: str
	filetype: str
	url: Optional[str] = None
	language: str

	class Config:
		schema_extra = {
			"example": {
				"filename": "requirements.txt",
				"filetype": "text/plain",
				"url": "https://example.com/requirements.txt",
				"language": "en"
			}
		}

class AppContentModel(BaseModel):
	id: Optional[str] = Field(alias="_id", default=None)
	appId: str
	contentType: Literal["qa", "note", "url", "document"]
	content: dict
	embedding: Optional[List[float]] = None
	sourceRef: Optional[str] = None
	createdAt: Optional[datetime] = Field(default_factory=datetime.utcnow)
	updatedAt: Optional[datetime] = Field(default_factory=datetime.utcnow)

	class Config:
		schema_extra = {
			"example": {
				"_id": "c1d2e3f4-5678-1234-9abc-def012345678",
				"appId": "a1b2c3d4-e5f6-7a8b-9c0d-e1f2a3b4c5d6",
				"contentType": "qa",
				"content": {
					"question": "What is an embedding?",
					"answer": "An embedding is a vector representation of data.",
					"language": "en"
				},
				"embedding": [0.1, 0.2, 0.3],
				"sourceRef": "external_source_1",
				"createdAt": "2025-08-23T12:00:00Z",
				"updatedAt": "2025-08-23T12:00:00Z"
			}
		}
