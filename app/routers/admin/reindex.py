
from fastapi import APIRouter, HTTPException
from fastapi import BackgroundTasks
from app.db import app_content_collection, app_collection
import base64
def decrypt_api_key(enc_key: str) -> str:
	return base64.b64decode(enc_key.encode()).decode()
from app.utils.helpers import get_valid_api_key, safe_generate_embedding

router = APIRouter(prefix="/api/v1/admin/app/{app_id}/train", tags=["Admin Train"])

async def reindex_content(app_id: str):
	app = await app_collection.find_one({"_id": app_id})
	try:
		google_api_key = get_valid_api_key(app)
	except HTTPException:
		return 0
	# Fetch all content for this app
	cursor = app_content_collection.find({"app_id": app_id})
	count = 0
	async for doc in cursor:
		content_type = doc.get("contentType")
		content = doc.get("content", {})
		if content_type == "qa":
			text = f"{content.get('question', '')} {content.get('answer', '')}"
		elif content_type == "note":
			text = content.get("text", "")
		elif content_type == "url":
			text = content.get("url", "") + (" " + content.get("description", "") if content.get("description") else "")
		elif content_type == "document":
			text = content.get("filename", "") + (" " + content.get("url", "") if content.get("url") else "")
		else:
			continue
	embedding = await safe_generate_embedding(text, google_api_key)
	await app_content_collection.update_one({"_id": doc["_id"]}, {"$set": {"embedding": embedding}})
	count += 1
	return count

@router.post("", response_model=dict)
async def trigger_train(app_id: str, background_tasks: BackgroundTasks):
	# In real implementation, this would trigger async re-embedding
	background_tasks.add_task(reindex_content, app_id)
	return {"message": f"Training (re-indexing) triggered for app_id={app_id}"}
