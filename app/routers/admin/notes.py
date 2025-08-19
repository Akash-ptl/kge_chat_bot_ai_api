

from fastapi import APIRouter, HTTPException, Body
from ...db import app_content_collection
from ...models.content import NoteContent
from typing import List
from bson import ObjectId

router = APIRouter(prefix="/api/v1/admin/app/{appId}/notes", tags=["Admin Notes"])

def to_dict(obj):
	if isinstance(obj, dict):
		return {k: to_dict(v) for k, v in obj.items()}
	if isinstance(obj, list):
		return [to_dict(i) for i in obj]
	if isinstance(obj, ObjectId):
		return str(obj)
	return obj

# POST /api/v1/admin/app/{appId}/notes
@router.post("", response_model=dict)
async def create_note(appId: str, note: NoteContent = Body(...)):
	doc = {
		"appId": appId,
		"contentType": "note",
		"content": note.dict(),
	}
	result = await app_content_collection.insert_one(doc)
	return {"id": str(result.inserted_id)}

# GET /api/v1/admin/app/{appId}/notes
@router.get("", response_model=List[dict])
async def list_notes(appId: str):
	notes = await app_content_collection.find({"appId": appId, "contentType": "note"}).to_list(100)
	return [to_dict(n) for n in notes]

# PUT /api/v1/admin/app/{appId}/notes/{noteId}
@router.put("/{noteId}", response_model=dict)
async def update_note(appId: str, noteId: str, note: NoteContent = Body(...)):
	update_result = await app_content_collection.update_one(
		{"_id": ObjectId(noteId), "contentType": "note", "appId": appId},
		{"$set": {"content": note.dict()}}
	)
	if update_result.modified_count == 0:
		raise HTTPException(status_code=404, detail="Note not found or data unchanged")
	return {"message": "Note updated successfully"}

# DELETE /api/v1/admin/app/{appId}/notes/{noteId}
@router.delete("/{noteId}", response_model=dict)
async def delete_note(appId: str, noteId: str):
	delete_result = await app_content_collection.delete_one({"_id": ObjectId(noteId), "contentType": "note", "appId": appId})
	if delete_result.deleted_count == 0:
		raise HTTPException(status_code=404, detail="Note not found")
	return {"message": "Note deleted successfully"}
