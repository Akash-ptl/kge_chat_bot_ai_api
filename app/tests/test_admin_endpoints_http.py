import requests
import time

BASE_URL = "http://127.0.0.1:8000"

def wait_for_server():
    for _ in range(10):
        try:
            r = requests.get(f"{BASE_URL}/")
            if r.status_code == 200:
                return True
        except Exception:
            time.sleep(1)
    return False

def test_root():
    r = requests.get(f"{BASE_URL}/")
    assert r.status_code == 200
    assert r.json()["message"] == "Chatbot API is running"

def test_qna_crud():
    qna = {"question": "What is AI?", "answer": "Artificial Intelligence", "language": "en"}
    r = requests.post(f"{BASE_URL}/api/v1/admin/app/test_app/qa", json=qna)
    assert r.status_code == 200
    qna_id = r.json()["id"]
    r = requests.get(f"{BASE_URL}/api/v1/admin/app/test_app/qa")
    assert r.status_code == 200
    assert any(q["content"]["question"] == "What is AI?" for q in r.json())
    # No single GET endpoint for QnA in new RESTful design
    assert r.status_code == 200
    qna_update = {"question": "What is AI?", "answer": "AI means Artificial Intelligence", "language": "en"}
    r = requests.put(f"{BASE_URL}/api/v1/admin/app/test_app/qa/{qna_id}", json=qna_update)
    assert r.status_code == 200
    r = requests.delete(f"{BASE_URL}/api/v1/admin/app/test_app/qa/{qna_id}")
    assert r.status_code == 200

def test_notes_crud():
    note = {"text": "This is a note.", "language": "en"}
    r = requests.post(f"{BASE_URL}/api/v1/admin/app/test_app/notes", json=note)
    assert r.status_code == 200
    note_id = r.json()["id"]
    r = requests.get(f"{BASE_URL}/api/v1/admin/app/test_app/notes")
    assert r.status_code == 200
    assert any(n["content"]["text"] == "This is a note." for n in r.json())
    # No single GET endpoint for Notes in new RESTful design
    assert r.status_code == 200
    note_update = {"text": "Updated note.", "language": "en"}
    r = requests.put(f"{BASE_URL}/api/v1/admin/app/test_app/notes/{note_id}", json=note_update)
    assert r.status_code == 200
    r = requests.delete(f"{BASE_URL}/api/v1/admin/app/test_app/notes/{note_id}")
    assert r.status_code == 200

def test_urls_crud():
    url = {"url": "https://example.com", "description": "Example", "language": "en"}
    r = requests.post(f"{BASE_URL}/api/v1/admin/app/test_app/urls", json=url)
    assert r.status_code == 200
    url_id = r.json()["id"]
    r = requests.get(f"{BASE_URL}/api/v1/admin/app/test_app/urls")
    assert r.status_code == 200
    assert any(u["content"]["url"] == "https://example.com" for u in r.json())
    # No single GET endpoint for URLs in new RESTful design
    assert r.status_code == 200
    url_update = {"url": "https://example.com/updated", "description": "Updated", "language": "en"}
    r = requests.put(f"{BASE_URL}/api/v1/admin/app/test_app/urls/{url_id}", json=url_update)
    assert r.status_code == 200
    r = requests.delete(f"{BASE_URL}/api/v1/admin/app/test_app/urls/{url_id}")
    assert r.status_code == 200

def test_documents_crud():
    doc = {"filename": "file.pdf", "filetype": "pdf", "language": "en"}
    r = requests.post(f"{BASE_URL}/api/v1/admin/app/test_app/documents", json=doc)
    assert r.status_code == 200
    doc_id = r.json()["id"]
    r = requests.get(f"{BASE_URL}/api/v1/admin/app/test_app/documents")
    assert r.status_code == 200
    assert any(d["content"]["filename"] == "file.pdf" for d in r.json())
    # No single GET endpoint for Documents in new RESTful design
    assert r.status_code == 200
    doc_update = {"filename": "file2.pdf", "filetype": "pdf", "language": "en"}
    r = requests.put(f"{BASE_URL}/api/v1/admin/app/test_app/documents/{doc_id}", json=doc_update)
    assert r.status_code == 200
    r = requests.delete(f"{BASE_URL}/api/v1/admin/app/test_app/documents/{doc_id}")
    assert r.status_code == 200

def test_guardrail_crud():
    guardrail = {
        "ruleName": "No Spam",
        "ruleType": "blacklist_phrase",
        "pattern": "spam",
        "action": "block_input",
        "responseMessage": {"en": "No spam allowed."},
        "isActive": True,
        "appId": "test_app"
    }
    r = requests.post(f"{BASE_URL}/api/v1/admin/app/test_app/guardrails", json=guardrail)
    print('POST /admin/guardrail:', r.status_code, r.text)
    assert r.status_code == 200
    guardrail_id = r.json()["id"]
    r = requests.get(f"{BASE_URL}/api/v1/admin/app/test_app/guardrails")
    print('GET /admin/guardrail:', r.status_code, r.text)
    assert r.status_code == 200
    assert any(g["ruleName"] == "No Spam" for g in r.json())
    r = requests.get(f"{BASE_URL}/api/v1/admin/app/test_app/guardrails/{guardrail_id}")
    print('GET /admin/guardrail/{id}:', r.status_code, r.text)
    assert r.status_code == 200
    guardrail_update = guardrail.copy()
    guardrail_update["ruleName"] = "No Spam Updated"
    r = requests.put(f"{BASE_URL}/api/v1/admin/app/test_app/guardrails/{guardrail_id}", json=guardrail_update)
    print('PUT /admin/guardrail/{id}:', r.status_code, r.text)
    assert r.status_code == 200
    r = requests.delete(f"{BASE_URL}/api/v1/admin/app/test_app/guardrails/{guardrail_id}")
    print('DELETE /admin/guardrail/{id}:', r.status_code, r.text)
    assert r.status_code == 200

def test_reindex():
    r = requests.post(f"{BASE_URL}/api/v1/admin/app/test_app/train")
    assert r.status_code == 200
    assert "Training (re-indexing) triggered" in r.json()["message"]

if __name__ == "__main__":
    assert wait_for_server(), "API server not running on http://127.0.0.1:8001"
    test_root()
    test_qna_crud()
    test_notes_crud()
    test_urls_crud()
    test_documents_crud()
    test_guardrail_crud()
    test_reindex()
    print("All HTTP endpoint tests passed!")
