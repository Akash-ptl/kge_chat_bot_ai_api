# app/routers/admin/app.py
from fastapi import APIRouter, HTTPException
from ...db import apps_collection
from ...models.app import AppModel

router = APIRouter(prefix="/api/v1/admin/app", tags=["App Admin - Apps"])

@router.post("/")
async def create_app(app: AppModel):
	app_dict = app.dict(by_alias=True)
	result = await apps_collection.insert_one(app_dict)
	return {"id": str(result.inserted_id)}

@router.get("/")
async def list_apps():
	apps = await apps_collection.find().to_list(100)
	return apps

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
