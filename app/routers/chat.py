def get_direct_qna_response(user_message, relevant_content):
    for c in relevant_content:
        if c.get("contentType") == "qa":
            q = c["content"].get("question", "").strip().lower()
            a = c["content"].get("answer", "")
            if user_message.strip().lower() == q:
                return a
    return None

def get_best_note_response(user_message, relevant_content, embedding):
    import numpy as np
    best_note = None
    best_sim = -1
    for c in relevant_content:
        if c.get("contentType") == "note" and c.get("embedding"):
            note_emb = np.array(c["embedding"])
            user_emb = np.array(embedding)
            if note_emb.size and user_emb.size:
                sim = float(np.dot(user_emb, note_emb) / (np.linalg.norm(user_emb) * np.linalg.norm(note_emb) + 1e-8))
                if sim > best_sim:
                    best_sim = sim
                    best_note = c
    if best_note and best_sim > 0.7:
        return best_note["content"].get("text", "")
    return None

def get_url_response(user_message, relevant_content):
    for c in relevant_content:
        if c.get("contentType") == "url":
            desc = c["content"].get("description", "").strip().lower()
            url_val = c["content"].get("url", "")
            if desc and desc in user_message.strip().lower():
                return url_val
            if url_val and url_val in user_message:
                return url_val
    return None

async def get_llm_response(user_message, relevant_content, last_msgs, best_note, best_sim, app, language, x_app_id):
    qna_context = []
    note_context = []
    url_context = []
    doc_context = []
    for c in relevant_content:
        if c.get("contentType") == "qa":
            qna_context.append(f"Q: {c['content'].get('question', '')}\nA: {c['content'].get('answer', '')}")
        elif c.get("contentType") == "note":
            note_text = c['content'].get('text', '')
            if best_note and c == best_note and best_sim > 0.4:
                note_context.append(f"[MOST RELEVANT NOTE]: {note_text}")
            else:
                note_context.append(f"Note: {note_text}")
        elif c.get("contentType") == "url":
            url_context.append(f"URL: {c['content'].get('url', '')}\nDescription: {c['content'].get('description', '')}")
        elif c.get("contentType") == "document":
            if c.get("extractedText"):
                doc_context.append(f"Document: {c['extractedText']}")
            else:
                doc_context.append(f"Document: {c['content'].get('filename', '')} {c['content'].get('url', '')}")
    prompt = build_prompt(user_message, qna_context, note_context, url_context, doc_context, last_msgs)
    logging.info("\n--- LLM Prompt ---\n" + prompt[:2000] + ("..." if len(prompt) > 2000 else "") + "\n--- End Prompt ---\n")
    ai_response = await call_gemma_api(app["googleApiKey"], prompt, model="gemini-1.5-flash")
    if isinstance(ai_response, dict) and ai_response.get("error"):
        raise HTTPException(status_code=502, detail=ai_response)
    guardrail_result_out = await apply_guardrails(x_app_id, ai_response, language, direction="output")
    if guardrail_result_out["blocked"]:
        ai_response = guardrail_result_out["message"]
    return ai_response

async def store_message_and_response(x_app_id, session, user_message, ai_response, language):
    now = datetime.datetime.now(datetime.timezone.utc)
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
    await chat_sessions_collection.update_one({"_id": session["_id"]}, {"$set": {"lastActiveAt": now, "language": language}})
    return now
PROMPT_SEPARATOR = "\n---\n"
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

def detect_language_switch(user_message_lower, switch_phrases):
    for phrase, lang in switch_phrases:
        if phrase in user_message_lower:
            return lang
    return None

def detect_thank_you(user_message_lower, thank_you_phrases):
    return any(phrase in user_message_lower for phrase in thank_you_phrases)

def build_prompt(user_message, qna_context, note_context, url_context, doc_context, last_msgs):
    prompt = (
        "You are an expert assistant. Answer the user's question strictly using ONLY the provided context below. "
        "If the answer is not present, reply 'I don't know based on the provided context.'\n"
        f"User Question: {user_message}\n"
    )
    if qna_context:
        prompt += "\nQ&A Knowledge Base:\n" + PROMPT_SEPARATOR.join(qna_context)
    if note_context:
        prompt += "\nNotes:\n" + PROMPT_SEPARATOR.join(note_context)
    if url_context:
        prompt += "\nURLs:\n" + PROMPT_SEPARATOR.join(url_context)
    if doc_context:
        prompt += "\nDocuments:\n" + PROMPT_SEPARATOR.join(doc_context)
    if last_msgs:
        prompt += "\n\nChat History:\n" + "\n".join([m["message"] for m in last_msgs])
    return prompt

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
    now = datetime.datetime.now(datetime.timezone.utc)
    session = {
        "_id": new_session_id,
        "appId": app_id,
        "startedAt": now,
        "lastActiveAt": now,
        "status": "active",
        "language": None
    }
    await chat_sessions_collection.insert_one(session)
    return session


def _guardrail_result(blocked, rule, response_msg):
    return {"blocked": blocked, "ruleId": str(rule["_id"]), "message": response_msg}

def _evaluate_rule(rule, text, language, direction):
    rule_type = rule.get("ruleType")
    pattern = rule.get("pattern", "")
    action = rule.get("action", "block_input")
    response_msg = rule.get("responseMessage", {}).get(language, "Blocked by guardrail.")
    if rule_type == "blacklist_phrase" and pattern in text:
        if action in ("block_input", "override_response"):
            return _guardrail_result(True, rule, response_msg)
        elif action == "log_only":
            return _guardrail_result(False, rule, response_msg)
    if rule_type == "topic_restriction" and pattern in text:
        if action in ("block_input", "override_response"):
            return _guardrail_result(True, rule, response_msg)
        elif action == "log_only":
            return _guardrail_result(False, rule, response_msg)
    if direction == "output" and rule_type == "response_filter" and pattern in text:
        if action in ("override_response", "block_input"):
            return _guardrail_result(True, rule, response_msg)
        elif action == "log_only":
            return _guardrail_result(False, rule, response_msg)
    return None

async def apply_guardrails(app_id: str, text: str, language: str, direction: str = "input"):
    guardrails = await app_guardrails_collection.find({"appId": app_id, "isActive": True}).to_list(100)
    for rule in guardrails:
        result = _evaluate_rule(rule, text, language, direction)
        if result is not None:
            return result
    return {"blocked": False}

async def get_relevant_content(app_id: str, embedding: list, limit: int = 5):
    # Vector similarity search using embedding (cosine similarity)
    from numpy import dot
    from numpy.linalg import norm
    import numpy as np
    # Always include all Q&A, Note, and URL entries for the app
    qnas = await app_content_collection.find({"appId": app_id, "contentType": "qa"}).to_list(100)
    notes = await app_content_collection.find({"appId": app_id, "contentType": "note"}).to_list(100)
    urls = await app_content_collection.find({"appId": app_id, "contentType": "url"}).to_list(100)
    # For documents, use similarity search
    docs = []
    if embedding:
        doc_candidates = await app_content_collection.find({"appId": app_id, "contentType": "document", "embedding": {"$exists": True}}).to_list(100)
        scored = []
        emb = np.array(embedding)
        for d in doc_candidates:
            doc_emb = np.array(d.get("embedding", []))
            if doc_emb.size == 0:
                continue
            sim = float(dot(emb, doc_emb) / (norm(emb) * norm(doc_emb) + 1e-8))
            scored.append((sim, d))
        scored.sort(reverse=True, key=lambda x: x[0])
        docs = [d for sim, d in scored[:limit]]
    else:
        docs = await app_content_collection.find({"appId": app_id, "contentType": "document"}).sort("updatedAt", -1).to_list(limit)
    # Combine all for context
    return qnas + notes + urls + docs

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
    lang_switch = detect_language_switch(user_message_lower, switch_phrases)
    if lang_switch:
        language = lang_switch
        await chat_sessions_collection.update_one({"_id": session["_id"]}, {"$set": {"language": lang_switch}})

    # 2. Welcome message on new session
    is_new_session = not x_session_id or not session.get("lastActiveAt")
    if is_new_session:
        welcome = app.get("welcomeMessage", {}).get(language, "Welcome!")
        now = datetime.datetime.now(datetime.timezone.utc)
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
    if detect_thank_you(user_message_lower, thank_you_phrases):
        ack = app.get("acknowledgmentMessage", {}).get(language, "You're welcome!")
        now = datetime.datetime.now(datetime.timezone.utc)
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

    ai_response = get_direct_qna_response(user_message, relevant_content)
    best_note = None
    best_sim = -1
    if ai_response is None:
        ai_response = get_best_note_response(user_message, relevant_content, embedding)
    if ai_response is None:
        ai_response = get_url_response(user_message, relevant_content)
    if ai_response is None:
        ai_response = await get_llm_response(user_message, relevant_content, last_msgs, best_note, best_sim, app, language, x_app_id)
        guardrail_result_out = await apply_guardrails(x_app_id, ai_response, language, direction="output")
    else:
        guardrail_result_out = await apply_guardrails(x_app_id, ai_response, language, direction="output")
    if guardrail_result_out["blocked"]:
        ai_response = guardrail_result_out["message"]
    await store_message_and_response(x_app_id, session, user_message, ai_response, language)
    return ChatMessageResponse(
        sessionId=session["_id"],
        message=ai_response,
        guardrailTriggered=guardrail_result_out["blocked"],
        guardrailRuleId=guardrail_result_out.get("ruleId"),
        language=language
    )
