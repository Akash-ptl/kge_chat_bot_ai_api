

from fastapi import APIRouter, HTTPException, Body
from app.db import app_content_collection
from ...models.content import URLContent
from typing import List
import uuid

router = APIRouter(prefix="/api/v1/admin/app/{appId}/urls", tags=["Admin URLs"])

def to_dict(obj):
	if isinstance(obj, dict):
		return {k: to_dict(v) for k, v in obj.items()}
	if isinstance(obj, list):
		return [to_dict(i) for i in obj]
	# No ObjectId conversion needed; all IDs are strings
	return obj

# POST /api/v1/admin/app/{appId}/urls
@router.post("", response_model=dict)
async def create_url(appId: str, url: URLContent = Body(...)):
	doc = {
		"_id": str(uuid.uuid4()),
		"appId": appId,
		"contentType": "url",
		"content": url.dict(),
	}
	result = await app_content_collection.insert_one(doc)
	return {"id": doc["_id"]}

# GET /api/v1/admin/app/{appId}/urls
@router.get("", response_model=List[dict])
async def list_urls(appId: str):
	urls = await app_content_collection.find({"appId": appId, "contentType": "url"}).to_list(100)
	return [to_dict(u) for u in urls] if urls else []

# PUT /api/v1/admin/app/{appId}/urls/{urlId}
@router.put("/{urlId}", response_model=dict)
async def update_url(appId: str, urlId: str, url: URLContent = Body(...)):
	update_result = await app_content_collection.update_one(
		{"_id": urlId, "contentType": "url", "appId": appId},
		{"$set": {"content": url.dict()}}
	)
	if update_result.modified_count == 0:
		raise HTTPException(status_code=404, detail="URL not found or data unchanged")
	return {"message": "URL updated successfully"}

# DELETE /api/v1/admin/app/{appId}/urls/{urlId}
@router.delete("/{urlId}", response_model=dict)
async def delete_url(appId: str, urlId: str):
	delete_result = await app_content_collection.delete_one({"_id": urlId, "contentType": "url", "appId": appId})
	if delete_result.deleted_count == 0:
		raise HTTPException(status_code=404, detail="URL not found")
	return {"message": "URL deleted successfully"}
