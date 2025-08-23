# app/routers/chat.py
from fastapi import APIRouter, Request, Header, HTTPException, Body
from typing import Optional, Dict
from pydantic import BaseModel, Field
class ChatMessageRequest(BaseModel):
    message: str = Field(..., example="Hello, how can I use your service?")

class ChatMessageResponse(BaseModel):
    sessionId: str = Field(..., example="b7e6c2e2-8c2e-4b7e-9c2e-8c2e4b7e9c2e")
    message: str = Field(..., example="Hi! How can I help you today?")
    guardrailTriggered: bool = Field(..., example=False)
    guardrailRuleId: Optional[str] = Field(None, example="a1b2c3d4-e5f6-7a8b-9c0d-e1f2a3b4c5d6")
from uuid import uuid4
from app.db import app_collection, chat_sessions_collection, chat_messages_collection, app_content_collection, app_guardrails_collection
import httpx
import datetime

router = APIRouter(prefix="/api/v1/chat", tags=["Chat User"])

async def get_app(app_id: str):
    app = await app_collection.find_one({"_id": app_id})
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    return app

async def get_session(app_id: str, session_id: Optional[str]):
    if session_id:
        session = await chat_sessions_collection.find_one({"_id": session_id, "appId": app_id})
        if session:
            return session
    # Create new session
    new_session_id = str(uuid4())
    session = {
        "_id": new_session_id,
        "appId": app_id,
        "startedAt": datetime.datetime.utcnow(),
        "lastActiveAt": datetime.datetime.utcnow(),
        "status": "active",
        "language": None
    }
    await chat_sessions_collection.insert_one(session)
    return session

async def apply_guardrails(app_id: str, text: str, language: str, direction: str = "input"):
    # direction: "input" or "output"
    guardrails = await app_guardrails_collection.find({"appId": app_id, "isActive": True}).to_list(100)
    for rule in guardrails:
        if rule["ruleType"] == "blacklist_phrase" and rule["pattern"] in text:
            return {
                "blocked": True,
                "ruleId": str(rule["_id"]),
                "message": rule["responseMessage"].get(language, "Blocked by guardrail.")
            }
    return {"blocked": False}

async def get_relevant_content(app_id: str, embedding: list, limit: int = 5):
    # Placeholder: fetch most recent content for now
    docs = await app_content_collection.find({"appId": app_id}).sort("updatedAt", -1).to_list(limit)
    return docs

async def get_last_messages(app_id: str, session_id: str, limit: int = 10):
    msgs = await chat_messages_collection.find({"appId": app_id, "sessionId": session_id}).sort("timestamp", -1).to_list(limit)
    return list(reversed(msgs))

async def call_gemma_api(api_key: str, prompt: str, model: str = "gemini-1.5-flash", temperature: float = 0.2, max_tokens: int = 512):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens}
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload)
        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            # Return error details for 400/404
            return {"error": f"Gemma API error: {exc.response.status_code} {exc.response.reason_phrase}", "details": exc.response.text}
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

@router.post("/message", response_model=ChatMessageResponse)
async def chat_message(request: Request, body: ChatMessageRequest = Body(...), x_app_id: str = Header(...), x_session_id: Optional[str] = Header(None)):
    app = await get_app(x_app_id)
    session = await get_session(x_app_id, x_session_id)
    language = session.get("language") or app.get("defaultLanguage", "en")
    user_message = body.message
    if not user_message:
        raise HTTPException(status_code=400, detail="Message required")
    # Input guardrails
    guardrail_result = await apply_guardrails(x_app_id, user_message, language, direction="input")
    if guardrail_result["blocked"]:
        return ChatMessageResponse(
            sessionId=session["_id"],
            message=guardrail_result["message"],
            guardrailTriggered=True,
            guardrailRuleId=guardrail_result["ruleId"]
        )
    # Placeholder: embedding = []
    embedding = []
    relevant_content = await get_relevant_content(x_app_id, embedding)
    last_msgs = await get_last_messages(x_app_id, session["_id"])
    prompt = user_message + "\n" + "\n".join([c["content"].get("question", "") + " " + c["content"].get("answer", "") for c in relevant_content])
    prompt += "\n" + "\n".join([m["message"] for m in last_msgs])
    ai_response = await call_gemma_api(app["googleApiKey"], prompt, model="gemini-1.5-flash")
    if isinstance(ai_response, dict) and ai_response.get("error"):
        # Return a user-friendly error if Gemma API fails
        raise HTTPException(status_code=502, detail=ai_response)
    # Output guardrails
    guardrail_result_out = await apply_guardrails(x_app_id, ai_response, language, direction="output")
    if guardrail_result_out["blocked"]:
        ai_response = guardrail_result_out["message"]
    # Store message and response
    now = datetime.datetime.utcnow()
    await chat_messages_collection.insert_one({
        "appId": x_app_id,
        "sessionId": session["_id"],
        "sender": "user",
        "message": user_message,
        "timestamp": now,
        "language": language
    })
    await chat_messages_collection.insert_one({
        "appId": x_app_id,
        "sessionId": session["_id"],
        "sender": "ai",
        "message": ai_response,
        "timestamp": now,
        "language": language
    })
    # Update session last active
    await chat_sessions_collection.update_one({"_id": session["_id"]}, {"$set": {"lastActiveAt": now}})
    return ChatMessageResponse(
        sessionId=session["_id"],
        message=ai_response,
        guardrailTriggered=guardrail_result_out["blocked"],
        guardrailRuleId=guardrail_result_out.get("ruleId")
    )
