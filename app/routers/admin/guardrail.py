

from fastapi import APIRouter, HTTPException, Body
from app.db import guardrails_collection
from ...models.guardrail import GuardrailModel
from typing import List
import uuid

router = APIRouter(prefix="/api/v1/admin/app/{app_id}/guardrails", tags=["Admin Guardrail"])

def to_dict(obj):
	if isinstance(obj, dict):
		return {k: to_dict(v) for k, v in obj.items()}
	if isinstance(obj, list):
		return [to_dict(i) for i in obj]
	# No ObjectId conversion needed; all IDs are strings
	return obj

# POST /api/v1/admin/app/{appId}/guardrails
@router.post("", response_model=dict)
async def create_guardrail(app_id: str, guardrail: GuardrailModel = Body(...)):
	doc = guardrail.dict(by_alias=True)
	doc["app_id"] = app_id
	doc["_id"] = str(uuid.uuid4())
	await guardrails_collection.insert_one(doc)
	return {"id": doc["_id"]}

# GET /api/v1/admin/app/{appId}/guardrails
@router.get("", response_model=List[dict])
async def list_guardrails(app_id: str):
	guards = await guardrails_collection.find({"app_id": app_id}).to_list(100)
	return [to_dict(g) for g in guards] if guards else []

# GET /api/v1/admin/app/{appId}/guardrails/{rule_id}
@router.get("/{rule_id}", response_model=dict)
async def get_guardrail(app_id: str, rule_id: str):
	guard = await guardrails_collection.find_one({"_id": rule_id, "app_id": app_id})
	if not guard:
		raise HTTPException(status_code=404, detail="Guardrail not found")
	return to_dict(guard)

# PUT /api/v1/admin/app/{appId}/guardrails/{rule_id}
@router.put("/{rule_id}", response_model=dict)
async def update_guardrail(app_id: str, rule_id: str, guardrail: GuardrailModel = Body(...)):
	update_result = await guardrails_collection.update_one(
		{"_id": rule_id, "app_id": app_id},
		{"$set": guardrail.dict(exclude_unset=True, by_alias=True)}
	)
	if update_result.modified_count == 0:
		raise HTTPException(status_code=404, detail="Guardrail not found or data unchanged")
	return {"message": "Guardrail updated successfully"}

# DELETE /api/v1/admin/app/{appId}/guardrails/{rule_id}
@router.delete("/{rule_id}", response_model=dict)
async def delete_guardrail(app_id: str, rule_id: str):
	delete_result = await guardrails_collection.delete_one({"_id": rule_id, "app_id": app_id})
	if delete_result.deleted_count == 0:
		raise HTTPException(status_code=404, detail="Guardrail not found")
	return {"message": "Guardrail deleted successfully"}
