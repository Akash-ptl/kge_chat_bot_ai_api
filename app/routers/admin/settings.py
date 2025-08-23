# app/routers/admin/settings.py
from fastapi import APIRouter, HTTPException, Body
from app.db import app_collection
from typing import Dict, List

router = APIRouter(prefix="/api/v1/admin/app/{appId}/settings", tags=["Admin Settings"])

@router.put("/welcome-message", response_model=dict)
async def update_welcome_message(appId: str, welcomeMessage: Dict[str, str] = Body(...)):
    result = await app_collection.update_one({"_id": appId}, {"$set": {"welcomeMessage": welcomeMessage}})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="App not found or message unchanged")
    return {"message": "Welcome message updated"}

@router.put("/languages", response_model=dict)
async def update_languages(appId: str, languages: List[str] = Body(...)):
    result = await app_collection.update_one({"_id": appId}, {"$set": {"availableLanguages": languages}})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="App not found or languages unchanged")
    return {"message": "Languages updated"}

@router.put("/google-api-key", response_model=dict)
async def update_google_api_key(appId: str, googleApiKey: str = Body(...)):
    result = await app_collection.update_one({"_id": appId}, {"$set": {"googleApiKey": googleApiKey}})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="App not found or key unchanged")
    return {"message": "Google API key updated"}
