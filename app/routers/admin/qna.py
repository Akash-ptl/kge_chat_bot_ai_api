

from fastapi import APIRouter, HTTPException, Body
from app.db import app_content_collection
from ...models.content import QnAContent
from typing import List
import uuid

router = APIRouter(prefix="/api/v1/admin/app/{appId}/qa", tags=["Admin QnA"])

def to_dict(obj):
	if isinstance(obj, dict):
		return {k: to_dict(v) for k, v in obj.items()}
	if isinstance(obj, list):
		return [to_dict(i) for i in obj]
	# No ObjectId conversion needed; all IDs are strings
	return obj

@router.post("", response_model=dict)
async def create_qna(appId: str, qna: QnAContent = Body(...)):
	doc = {
		"_id": str(uuid.uuid4()),
		"appId": appId,
		"contentType": "qa",
		"content": qna.dict(),
	}
	result = await app_content_collection.insert_one(doc)
	return {"id": doc["_id"]}

# GET /api/v1/admin/app/{appId}/qa
@router.get("", response_model=List[dict])
async def list_qna(appId: str):
	qnas = await app_content_collection.find({"appId": appId, "contentType": "qa"}).to_list(100)
	return [to_dict(q) for q in qnas] if qnas else []

# PUT /api/v1/admin/app/{appId}/qa/{qaId}
@router.put("/{qaId}", response_model=dict)
async def update_qna(appId: str, qaId: str, qna: QnAContent = Body(...)):
	update_result = await app_content_collection.update_one(
		{"_id": qaId, "contentType": "qa", "appId": appId},
		{"$set": {"content": qna.dict()}}
	)
	if update_result.modified_count == 0:
		raise HTTPException(status_code=404, detail="QnA not found or data unchanged")
	return {"message": "QnA updated successfully"}

# DELETE /api/v1/admin/app/{appId}/qa/{qaId}
@router.delete("/{qaId}", response_model=dict)
async def delete_qna(appId: str, qaId: str):
	delete_result = await app_content_collection.delete_one({"_id": qaId, "contentType": "qa", "appId": appId})
	if delete_result.deleted_count == 0:
		raise HTTPException(status_code=404, detail="QnA not found")
	return {"message": "QnA deleted successfully"}
