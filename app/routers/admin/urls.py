

from fastapi import APIRouter, HTTPException, Body
from app.db import app_content_collection, app_collection
import base64
def decrypt_api_key(enc_key: str) -> str:
	try:
		return base64.b64decode(enc_key.encode()).decode()
	except Exception:
		return enc_key
from app.utils.helpers import get_valid_api_key, safe_generate_embedding, build_doc_dict
from ...models.content import URLContent
from typing import List
import uuid

router = APIRouter(prefix="/api/v1/admin/app/{app_id}/urls", tags=["Admin URLs"])

def to_dict(obj):
	if isinstance(obj, dict):
		return {k: to_dict(v) for k, v in obj.items()}
	if isinstance(obj, list):
		return [to_dict(i) for i in obj]
	# No ObjectId conversion needed; all IDs are strings
	return obj

 # POST /api/v1/admin/app/{app_id}/urls
@router.post("", response_model=dict)
async def create_url(app_id: str, url: URLContent = Body(...)):
	app = await app_collection.find_one({"_id": app_id})
	api_key = await get_valid_api_key(app)
	text = url.url + (" " + url.description if url.description else "")
	embedding = await safe_generate_embedding(text, api_key)
	doc = build_doc_dict(app_id, "url", url.dict(), embedding)
	await app_content_collection.insert_one(doc)
	return {"id": doc["_id"]}

 # GET /api/v1/admin/app/{app_id}/urls
@router.get("", response_model=List[dict])
async def list_urls(app_id: str):
	urls = await app_content_collection.find({"app_id": app_id, "contentType": "url"}).to_list(100)
	return [to_dict(u) for u in urls] if urls else []

 # PUT /api/v1/admin/app/{app_id}/urls/{urlId}
@router.put("/{url_id}", response_model=dict)
async def update_url(app_id: str, url_id: str, url: URLContent = Body(...)):
	app = await app_collection.find_one({"_id": app_id})
	api_key = await get_valid_api_key(app)
	text = url.url + (" " + url.description if url.description else "")
	embedding = await safe_generate_embedding(text, api_key)
	update_result = await app_content_collection.update_one(
		{"_id": url_id, "contentType": "url", "app_id": app_id},
		{"$set": {"content": url.dict(), "embedding": embedding}}
	)
	if update_result.modified_count == 0:
		raise HTTPException(status_code=404, detail="URL not found or data unchanged")
	return {"message": "URL updated successfully"}

 # DELETE /api/v1/admin/app/{app_id}/urls/{urlId}
@router.delete("/{url_id}", response_model=dict)
async def delete_url(app_id: str, url_id: str):
	# Remove the document and its embedding
	delete_result = await app_content_collection.delete_one({"_id": url_id, "contentType": "url", "app_id": app_id})
	if delete_result.deleted_count == 0:
		raise HTTPException(status_code=404, detail="URL not found")
	return {"message": "URL deleted successfully"}
