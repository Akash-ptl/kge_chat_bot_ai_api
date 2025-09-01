# app/routers/admin/settings.py

from fastapi import APIRouter, HTTPException, Body
from app.db import app_collection
from typing import Dict, List
import base64

router = APIRouter(prefix="/api/v1/admin/app/{app_id}/settings", tags=["Admin Settings"])

@router.put("/welcome-message", response_model=dict)
async def update_welcome_message(app_id: str, welcome_message: Dict[str, str] = Body(...)):
    update_result = await app_collection.update_one({"_id": app_id}, {"$set": {"welcomeMessage": welcome_message}})
    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="App not found or message unchanged")
    return {"message": "Welcome message updated"}


# New endpoint to update both availableLanguages and defaultLanguage
@router.put("/languages-settings", response_model=dict)
async def update_languages_settings(app_id: str, available_languages: List[str] = Body(...), default_language: str = Body(...)):
    update_result = await app_collection.update_one(
        {"_id": app_id},
        {"$set": {"availableLanguages": available_languages, "defaultLanguage": default_language}}
    )
    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="App not found or settings unchanged")
    return {"message": "Languages and default language updated"}


# Simple base64 encoding as a placeholder for encryption (replace with real encryption in production)
def encrypt_api_key(api_key: str) -> str:
    return base64.b64encode(api_key.encode()).decode()

def decrypt_api_key(enc_key: str) -> str:
    return base64.b64decode(enc_key.encode()).decode()

@router.put("/google-api-key", response_model=dict)
async def update_google_api_key(app_id: str, google_api_key: str = Body(...)):
    encrypted_key = encrypt_api_key(google_api_key)
    update_result = await app_collection.update_one({"_id": app_id}, {"$set": {"googleApiKey": encrypted_key}})
    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="App not found or key unchanged")
    return {"message": "Google API key updated"}
