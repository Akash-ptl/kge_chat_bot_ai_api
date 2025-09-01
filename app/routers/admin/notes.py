

from fastapi import APIRouter, HTTPException, Body
from app.db import app_content_collection, app_collection
import base64
def decrypt_api_key(enc_key: str) -> str:
	try:
		return base64.b64decode(enc_key.encode()).decode()
	except Exception:
		return enc_key
from app.services.embedding import generate_embedding
from ...models.content import NoteContent
from typing import List
import uuid

router = APIRouter(prefix="/api/v1/admin/app/{app_id}/notes", tags=["Admin Notes"])

def to_dict(obj):
	if isinstance(obj, dict):
		return {k: to_dict(v) for k, v in obj.items()}
	if isinstance(obj, list):
		return [to_dict(i) for i in obj]
	# No ObjectId conversion needed; all IDs are strings
	return obj

 # POST /api/v1/admin/app/{app_id}/notes
@router.post("", response_model=dict)
async def create_note(app_id: str, note: NoteContent = Body(...)):
	app = await app_collection.find_one({"_id": app_id})
	if not app or not app.get("googleApiKey"):
		raise HTTPException(status_code=400, detail="App or Google API key not found")
	text = note.text
	api_key = decrypt_api_key(app["googleApiKey"])
	try:
		embedding = await generate_embedding(text, api_key)
	except Exception:
		# Raise HTTPException so FastAPI returns a JSON error response
		raise HTTPException(status_code=500, detail="Embedding error")
	doc = {
		"_id": str(uuid.uuid4()),
		"app_id": app_id,
		"contentType": "note",
		"content": note.dict(),
		"embedding": embedding
	}
	await app_content_collection.insert_one(doc)
	return {"id": doc["_id"]}

 # GET /api/v1/admin/app/{app_id}/notes
@router.get("", response_model=List[dict])
async def list_notes(app_id: str):
	notes = await app_content_collection.find({"app_id": app_id, "contentType": "note"}).to_list(100)
	return [to_dict(n) for n in notes] if notes else []

 # PUT /api/v1/admin/app/{app_id}/notes/{noteId}
@router.put("/{note_id}", response_model=dict)
async def update_note(app_id: str, note_id: str, note: NoteContent = Body(...)):
	app = await app_collection.find_one({"_id": app_id})
	if not app or not app.get("googleApiKey"):
		raise HTTPException(status_code=400, detail="App or Google API key not found")
	text = note.text
	api_key = decrypt_api_key(app["googleApiKey"])
	embedding = await generate_embedding(text, api_key)
	update_result = await app_content_collection.update_one(
		{"_id": note_id, "contentType": "note", "app_id": app_id},
		{"$set": {"content": note.dict(), "embedding": embedding}}
	)
	if update_result.modified_count == 0:
		raise HTTPException(status_code=404, detail="Note not found or data unchanged")
	return {"message": "Note updated successfully"}

 # DELETE /api/v1/admin/app/{app_id}/notes/{noteId}
@router.delete("/{note_id}", response_model=dict)
async def delete_note(app_id: str, note_id: str):
	# Remove the document and its embedding
	delete_result = await app_content_collection.delete_one({"_id": note_id, "contentType": "note", "app_id": app_id})
	if delete_result.deleted_count == 0:
		raise HTTPException(status_code=404, detail="Note not found")
	return {"message": "Note deleted successfully"}
