

from fastapi import APIRouter, HTTPException, Body
from app.db import app_content_collection, app_collection
import base64
def decrypt_api_key(enc_key: str) -> str:
	try:
		return base64.b64decode(enc_key.encode()).decode()
	except Exception:
		return enc_key
from app.services.embedding import generate_embedding
from ...models.content import QnAContent
from typing import List
import uuid

router = APIRouter(prefix="/api/v1/admin/app/{appId}/qna", tags=["Admin QnA"])

def to_dict(obj):
	if isinstance(obj, dict):
		return {k: to_dict(v) for k, v in obj.items()}
	if isinstance(obj, list):
		return [to_dict(i) for i in obj]
	# No ObjectId conversion needed; all IDs are strings
	return obj

@router.post("", response_model=dict)
async def create_qna(appId: str, qna: QnAContent = Body(...)):
	app = await app_collection.find_one({"_id": appId})
	if not app or not app.get("googleApiKey"):
		raise HTTPException(status_code=400, detail="App or Google API key not found")
	text = f"{qna.question} {qna.answer}"
	api_key = decrypt_api_key(app["googleApiKey"])
	embedding = await generate_embedding(text, api_key)
	doc = {
		"_id": str(uuid.uuid4()),
		"appId": appId,
		"contentType": "qa",
		"content": qna.dict(),
		"embedding": embedding
	}
	result = await app_content_collection.insert_one(doc)
	return {"id": doc["_id"]}

@router.get("", response_model=List[dict])
async def list_qna(appId: str):
	qnas = await app_content_collection.find({"appId": appId, "contentType": "qa"}).to_list(100)
	return [to_dict(q) for q in qnas] if qnas else []

@router.put("/{qaId}", response_model=dict)
async def update_qna(appId: str, qaId: str, qna: QnAContent = Body(...)):
	app = await app_collection.find_one({"_id": appId})
	if not app or not app.get("googleApiKey"):
		raise HTTPException(status_code=400, detail="App or Google API key not found")
	text = f"{qna.question} {qna.answer}"
	api_key = decrypt_api_key(app["googleApiKey"])
	embedding = await generate_embedding(text, api_key)
	update_result = await app_content_collection.update_one(
		{"_id": qaId, "contentType": "qa", "appId": appId},
		{"$set": {"content": qna.dict(), "embedding": embedding}}
	)
	if update_result.modified_count == 0:
		raise HTTPException(status_code=404, detail="QnA not found or data unchanged")
	return {"message": "QnA updated successfully"}

@router.delete("/{qaId}", response_model=dict)
async def delete_qna(appId: str, qaId: str):
	# Remove the document and its embedding
	delete_result = await app_content_collection.delete_one({"_id": qaId, "contentType": "qa", "appId": appId})
	if delete_result.deleted_count == 0:
		raise HTTPException(status_code=404, detail="QnA not found")
	return {"message": "QnA deleted successfully"}
