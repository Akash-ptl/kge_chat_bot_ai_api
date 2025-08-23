import asyncio
import sys

if sys.platform.startswith("darwin") and sys.version_info >= (3, 8):
    asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

import pytest
import httpx
from app.main import app
from httpx import ASGITransport


@pytest.mark.asyncio
async def test_root():
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/")
        assert resp.status_code == 200
        assert resp.json()["message"] == "Chatbot API is running"


@pytest.mark.asyncio
async def test_qna_crud():
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        # Create
        qna = {"question": "What is AI?", "answer": "Artificial Intelligence", "language": "en"}
        resp = await ac.post("/api/v1/admin/app/test_app/qa", json=qna)
        assert resp.status_code == 200
        qna_id = resp.json()["id"]
        # List
        resp = await ac.get("/api/v1/admin/app/test_app/qa")
        assert resp.status_code == 200
        assert any(q["content"]["question"] == "What is AI?" for q in resp.json())
        # No single GET endpoint for QnA in new RESTful design
        # Update
        qna_update = {"question": "What is AI?", "answer": "AI means Artificial Intelligence", "language": "en"}
        resp = await ac.put(f"/api/v1/admin/app/test_app/qa/{qna_id}", json=qna_update)
        assert resp.status_code == 200
        # Delete
        resp = await ac.delete(f"/api/v1/admin/app/test_app/qa/{qna_id}")
        assert resp.status_code == 200

@pytest.mark.asyncio
async def test_notes_crud():
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        note = {"text": "This is a note.", "language": "en"}
        resp = await ac.post("/api/v1/admin/app/test_app/notes", json=note)
        assert resp.status_code == 200
        note_id = resp.json()["id"]
        resp = await ac.get("/api/v1/admin/app/test_app/notes")
        assert resp.status_code == 200
        assert any(n["content"]["text"] == "This is a note." for n in resp.json())
        # No single GET endpoint for Notes in new RESTful design
        note_update = {"text": "Updated note.", "language": "en"}
        resp = await ac.put(f"/api/v1/admin/app/test_app/notes/{note_id}", json=note_update)
        assert resp.status_code == 200
        resp = await ac.delete(f"/api/v1/admin/app/test_app/notes/{note_id}")
        assert resp.status_code == 200

@pytest.mark.asyncio
async def test_urls_crud():
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        url = {"url": "https://example.com", "description": "Example", "language": "en"}
        resp = await ac.post("/api/v1/admin/app/test_app/urls", json=url)
        assert resp.status_code == 200
        url_id = resp.json()["id"]
        resp = await ac.get("/api/v1/admin/app/test_app/urls")
        assert resp.status_code == 200
        assert any(u["content"]["url"] == "https://example.com" for u in resp.json())
        # No single GET endpoint for URLs in new RESTful design
        url_update = {"url": "https://example.com/updated", "description": "Updated", "language": "en"}
        resp = await ac.put(f"/api/v1/admin/app/test_app/urls/{url_id}", json=url_update)
        assert resp.status_code == 200
        resp = await ac.delete(f"/api/v1/admin/app/test_app/urls/{url_id}")
        assert resp.status_code == 200

@pytest.mark.asyncio
async def test_documents_crud():
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        doc = {"filename": "file.pdf", "filetype": "pdf", "language": "en"}
        resp = await ac.post("/api/v1/admin/app/test_app/documents", json=doc)
        assert resp.status_code == 200
        doc_id = resp.json()["id"]
        resp = await ac.get("/api/v1/admin/app/test_app/documents")
        assert resp.status_code == 200
        assert any(d["content"]["filename"] == "file.pdf" for d in resp.json())
        # No single GET endpoint for Documents in new RESTful design
        doc_update = {"filename": "file2.pdf", "filetype": "pdf", "language": "en"}
        resp = await ac.put(f"/api/v1/admin/app/test_app/documents/{doc_id}", json=doc_update)
        assert resp.status_code == 200
        resp = await ac.delete(f"/api/v1/admin/app/test_app/documents/{doc_id}")
        assert resp.status_code == 200

@pytest.mark.asyncio
async def test_guardrail_crud():
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        guardrail = {
            "ruleName": "No Spam",
            "ruleType": "blacklist_phrase",
            "pattern": "spam",
            "action": "block_input",
            "responseMessage": {"en": "No spam allowed."},
            "isActive": True,
            "appId": "test_app"
        }
        resp = await ac.post("/api/v1/admin/app/test_app/guardrails", json=guardrail)
        assert resp.status_code == 200
        guardrail_id = resp.json()["id"]
        resp = await ac.get("/api/v1/admin/app/test_app/guardrails")
        assert resp.status_code == 200
        assert any(g["ruleName"] == "No Spam" for g in resp.json())
        resp = await ac.get(f"/api/v1/admin/app/test_app/guardrails/{guardrail_id}")
        assert resp.status_code == 200
        guardrail_update = guardrail.copy()
        guardrail_update["ruleName"] = "No Spam Updated"
        resp = await ac.put(f"/api/v1/admin/app/test_app/guardrails/{guardrail_id}", json=guardrail_update)
        assert resp.status_code == 200
        resp = await ac.delete(f"/api/v1/admin/app/test_app/guardrails/{guardrail_id}")
        assert resp.status_code == 200

@pytest.mark.asyncio
async def test_reindex():
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post("/api/v1/admin/app/test_app/train")
        assert resp.status_code == 200
        assert "Training (re-indexing) triggered" in resp.json()["message"]
