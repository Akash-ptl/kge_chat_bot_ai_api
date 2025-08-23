# app/routers/admin/app.py
import uuid
from fastapi import APIRouter, HTTPException
from app.db import apps_collection
from ...models.app import AppModel

router = APIRouter(prefix="/api/v1/admin/app", tags=["App Admin - Apps"])

@router.post("/")
async def create_app(app: AppModel):
	doc = app.dict(by_alias=True)
	doc["_id"] = str(uuid.uuid4())
	result = await apps_collection.insert_one(doc)
	return {"id": doc["_id"]}

from typing import List

@router.get("/", response_model=List[AppModel])
async def list_apps():
	apps = await apps_collection.find().to_list(100)
	print("DEBUG: MongoDB returned:", apps)
	return apps if apps else []

@router.get("/{app_id}")
async def get_app(app_id: str):
	app = await apps_collection.find_one({"_id": app_id})
	if not app:
		raise HTTPException(status_code=404, detail="App not found")
	return app

@router.put("/{app_id}")
async def update_app(app_id: str, app: AppModel):
	update_result = await apps_collection.update_one(
		{"_id": app_id}, {"$set": app.dict(exclude_unset=True, by_alias=True)}
	)
	if update_result.modified_count == 0:
		raise HTTPException(status_code=404, detail="App not found or data unchanged")
	return {"message": "App updated successfully"}

@router.delete("/{app_id}")
async def delete_app(app_id: str):
	delete_result = await apps_collection.delete_one({"_id": app_id})
	if delete_result.deleted_count == 0:
		raise HTTPException(status_code=404, detail="App not found")
	return {"message": "App deleted successfully"}
