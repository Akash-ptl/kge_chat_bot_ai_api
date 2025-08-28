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
    language: str = Field(..., example="en")
from uuid import uuid4
from app.db import app_collection, chat_sessions_collection, chat_messages_collection, app_content_collection, app_guardrails_collection
import base64
import httpx
import logging
import datetime

router = APIRouter(prefix="/api/v1/chat", tags=["Chat User"])

def decrypt_api_key(enc_key: str) -> str:
    return base64.b64decode(enc_key.encode()).decode()

async def get_app(app_id: str):
    app = await app_collection.find_one({"_id": app_id})
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    # Decrypt Google API key if present
    if app.get("googleApiKey"):
        try:
            app["googleApiKey"] = decrypt_api_key(app["googleApiKey"])
        except Exception:
            pass
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
        rule_type = rule.get("ruleType")
        pattern = rule.get("pattern", "")
        action = rule.get("action", "block_input")
        response_msg = rule.get("responseMessage", {}).get(language, "Blocked by guardrail.")
        # Blacklist phrase
        if rule_type == "blacklist_phrase" and pattern in text:
            if action == "block_input":
                return {"blocked": True, "ruleId": str(rule["_id"]), "message": response_msg}
            elif action == "override_response":
                return {"blocked": True, "ruleId": str(rule["_id"]), "message": response_msg}
            elif action == "log_only":
                # Log only, do not block
                return {"blocked": False, "ruleId": str(rule["_id"]), "message": response_msg}
        # Topic restriction (simple substring match)
        if rule_type == "topic_restriction" and pattern in text:
            if action == "block_input":
                return {"blocked": True, "ruleId": str(rule["_id"]), "message": response_msg}
            elif action == "override_response":
                return {"blocked": True, "ruleId": str(rule["_id"]), "message": response_msg}
            elif action == "log_only":
                return {"blocked": False, "ruleId": str(rule["_id"]), "message": response_msg}
        # Response filter (for output)
        if direction == "output" and rule_type == "response_filter" and pattern in text:
            if action == "override_response":
                return {"blocked": True, "ruleId": str(rule["_id"]), "message": response_msg}
            elif action == "block_input":
                return {"blocked": True, "ruleId": str(rule["_id"]), "message": response_msg}
            elif action == "log_only":
                return {"blocked": False, "ruleId": str(rule["_id"]), "message": response_msg}
    return {"blocked": False}

async def get_relevant_content(app_id: str, embedding: list, limit: int = 5):
    # Vector similarity search using embedding (cosine similarity)
    from numpy import dot
    from numpy.linalg import norm
    import numpy as np
    if not embedding:
        # fallback: fetch most recent
        docs = await app_content_collection.find({"appId": app_id, "contentType": "document"}).sort("updatedAt", -1).to_list(limit)
        return docs
    # Fetch all document embeddings for this app
    docs = await app_content_collection.find({"appId": app_id, "contentType": "document", "embedding": {"$exists": True}}).to_list(100)
    scored = []
    emb = np.array(embedding)
    for d in docs:
        doc_emb = np.array(d.get("embedding", []))
        if doc_emb.size == 0:
            continue
        sim = float(dot(emb, doc_emb) / (norm(emb) * norm(doc_emb) + 1e-8))
        scored.append((sim, d))
    scored.sort(reverse=True, key=lambda x: x[0])
    return [d for sim, d in scored[:limit]]

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
    logging.info(f"[chat_message] Called with app_id={x_app_id} session_id={x_session_id} message={body.message}")
    app = await get_app(x_app_id)
    session = await get_session(x_app_id, x_session_id)
    language = session.get("language") or app.get("defaultLanguage", "en")
    user_message = body.message
    if not user_message:
        raise HTTPException(status_code=400, detail="Message required")

    # 1. Language switch detection (simple keyword-based)
    switch_phrases = [
        ("switch to spanish", "es"),
        ("speak in spanish", "es"),
        ("switch to french", "fr"),
        ("speak in french", "fr"),
        ("switch to english", "en"),
        ("speak in english", "en")
    ]
    user_message_lower = user_message.lower()
    switched = False
    for phrase, lang in switch_phrases:
        if phrase in user_message_lower:
            language = lang
            await chat_sessions_collection.update_one({"_id": session["_id"]}, {"$set": {"language": lang}})
            switched = True
            break

    # 2. Welcome message on new session
    is_new_session = not x_session_id or not session.get("lastActiveAt")
    if is_new_session:
        welcome = app.get("welcomeMessage", {}).get(language, "Welcome!")
        now = datetime.datetime.utcnow()
        await chat_messages_collection.insert_one({
            "appId": x_app_id,
            "sessionId": session["_id"],
            "sender": "ai",
            "message": welcome,
            "timestamp": now,
            "language": language
        })
        await chat_sessions_collection.update_one({"_id": session["_id"]}, {"$set": {"lastActiveAt": now}})
        return ChatMessageResponse(
            sessionId=session["_id"],
            message=welcome,
            guardrailTriggered=False,
            guardrailRuleId=None,
            language=language
        )

    # 3. Thank you/acknowledgment detection
    thank_you_phrases = ["thank you", "thanks", "thx", "gracias", "merci"]
    if any(phrase in user_message_lower for phrase in thank_you_phrases):
        ack = app.get("acknowledgmentMessage", {}).get(language, "You're welcome!")
        now = datetime.datetime.utcnow()
        await chat_messages_collection.insert_one({
            "appId": x_app_id,
            "sessionId": session["_id"],
            "sender": "ai",
            "message": ack,
            "timestamp": now,
            "language": language
        })
        await chat_sessions_collection.update_one({"_id": session["_id"]}, {"$set": {"lastActiveAt": now}})
        return ChatMessageResponse(
            sessionId=session["_id"],
            message=ack,
            guardrailTriggered=False,
            guardrailRuleId=None,
            language=language
        )

    # Input guardrails
    guardrail_result = await apply_guardrails(x_app_id, user_message, language, direction="input")
    if guardrail_result["blocked"]:
        return ChatMessageResponse(
            sessionId=session["_id"],
            message=guardrail_result["message"],
            guardrailTriggered=True,
            guardrailRuleId=guardrail_result["ruleId"],
            language=language
        )

    # Generate embedding for user message
    from app.services.embedding import generate_embedding
    embedding = await generate_embedding(user_message, app["googleApiKey"])
    relevant_content = await get_relevant_content(x_app_id, embedding)
    last_msgs = await get_last_messages(x_app_id, session["_id"])
    # Build prompt with extractedText from relevant documents (PDFs)
    doc_texts = []
    for c in relevant_content:
        if c.get("contentType") == "document":
            # Prefer extractedText if available, else fallback to content fields
            if c.get("extractedText"):
                doc_texts.append(f"Document: {c['extractedText']}")
            else:
                doc_texts.append(f"Document: {c['content'].get('filename', '')} {c['content'].get('url', '')}")
        elif c.get("contentType") == "qa":
            doc_texts.append(f"Q: {c['content'].get('question', '')}\nA: {c['content'].get('answer', '')}")
        elif c.get("contentType") == "note":
            doc_texts.append(f"Note: {c['content'].get('text', '')}")
        elif c.get("contentType") == "url":
            doc_texts.append(f"URL: {c['content'].get('url', '')} {c['content'].get('description', '')}")
    prompt = user_message
    if doc_texts:
        prompt += "\n\nContext:\n" + "\n---\n".join(doc_texts)
    if last_msgs:
        prompt += "\n\nChat History:\n" + "\n".join([m["message"] for m in last_msgs])
    logging.info("\n--- LLM Prompt ---\n" + prompt[:2000] + ("..." if len(prompt) > 2000 else "") + "\n--- End Prompt ---\n")
    logging.info("\n--- LLM Prompt ---\n" + prompt[:2000] + ("..." if len(prompt) > 2000 else "") + "\n--- End Prompt ---\n")
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
    # Update session last active and language
    await chat_sessions_collection.update_one({"_id": session["_id"]}, {"$set": {"lastActiveAt": now, "language": language}})
    return ChatMessageResponse(
        sessionId=session["_id"],
        message=ai_response,
        guardrailTriggered=guardrail_result_out["blocked"],
        guardrailRuleId=guardrail_result_out.get("ruleId"),
        language=language
    )
