

from fastapi import APIRouter, HTTPException, Body
from app.db import app_content_collection
from ...models.content import DocumentContent
from typing import List
import uuid

router = APIRouter(prefix="/api/v1/admin/app/{appId}/documents", tags=["Admin Documents"])

def to_dict(obj):
	if isinstance(obj, dict):
		return {k: to_dict(v) for k, v in obj.items()}
	if isinstance(obj, list):
		return [to_dict(i) for i in obj]
	# No ObjectId conversion needed; all IDs are strings
	return obj

# POST /api/v1/admin/app/{appId}/documents
@router.post("", response_model=dict)
async def create_document(appId: str, document: DocumentContent = Body(...)):
	doc = {
		"_id": str(uuid.uuid4()),
		"appId": appId,
		"contentType": "document",
		"content": document.dict(),
	}
	result = await app_content_collection.insert_one(doc)
	return {"id": doc["_id"]}

# GET /api/v1/admin/app/{appId}/documents
@router.get("", response_model=List[dict])
async def list_documents(appId: str):
	docs = await app_content_collection.find({"appId": appId, "contentType": "document"}).to_list(100)
	return [to_dict(d) for d in docs] if docs else []

# PUT /api/v1/admin/app/{appId}/documents/{documentId}
@router.put("/{documentId}", response_model=dict)
async def update_document(appId: str, documentId: str, document: DocumentContent = Body(...)):
	update_result = await app_content_collection.update_one(
		{"_id": documentId, "contentType": "document", "appId": appId},
		{"$set": {"content": document.dict()}}
	)
	if update_result.modified_count == 0:
		raise HTTPException(status_code=404, detail="Document not found or data unchanged")
	return {"message": "Document updated successfully"}

# DELETE /api/v1/admin/app/{appId}/documents/{documentId}
@router.delete("/{documentId}", response_model=dict)
async def delete_document(appId: str, documentId: str):
	delete_result = await app_content_collection.delete_one({"_id": documentId, "contentType": "document", "appId": appId})
	if delete_result.deleted_count == 0:
		raise HTTPException(status_code=404, detail="Document not found")
	return {"message": "Document deleted successfully"}
