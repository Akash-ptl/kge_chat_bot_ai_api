import requests
import json
import time

ADMIN_BASE_URL = "http://localhost:8000/api/v1/admin/app"
CHAT_BASE_URL = "http://localhost:8000/api/v1/chat/message"
GOOGLE_API_KEY = "AIzaSyDKzpg3Z8aLmY_lIoXRu7svHpDafmT_DhI"  # Use your real key if needed


def print_response(step, url, payload, response):
    print(f"\n--- {step} ---")
    print(f"URL: {url}")
    if payload is not None:
        print(f"Payload: {json.dumps(payload, indent=2)}")
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception:
        print(f"Raw Response: {response.text}")


def create_app():
    app_data = {
        "name": "Test Chatbot App",
        "description": "A valid app for chatbot API testing.",
        "defaultLanguage": "en",
        "availableLanguages": ["en", "es", "fr"],
        "welcomeMessage": {"en": "Welcome!", "es": "¡Bienvenido!", "fr": "Bienvenue!"},
        "acknowledgmentMessage": {"en": "You're welcome!", "es": "¡De nada!", "fr": "De rien!"},
        "googleApiKey": GOOGLE_API_KEY
    }
    resp = requests.post(ADMIN_BASE_URL + "/", json=app_data)
    print(f"Create App: {resp.status_code}")
    try:
        print(resp.json())
    except Exception:
        print(resp.text)
    if resp.status_code == 200 and "id" in resp.json():
        return resp.json()["id"]
    return None


def update_app_language(app_id, language="en"):
    url = f"{ADMIN_BASE_URL}/{app_id}"
    payload = {"defaultLanguage": language}
    resp = requests.put(url, json=payload)
    print_response("Update App Default Language", url, payload, resp)


def delete_app(app_id):
    url = f"{ADMIN_BASE_URL}/{app_id}"
    resp = requests.delete(url)
    print(f"Delete App: {resp.status_code}")
    try:
        print(resp.json())
    except Exception:
        print(resp.text)


def test_admin_crud(app_id):
    headers = {"Content-Type": "application/json", "X-App-ID": app_id}
    # Q&A CRUD
    qa_url = f"{ADMIN_BASE_URL}/{app_id}/qa"
    qa_payload = {"question": "What is AI?", "answer": "Artificial Intelligence", "language": "en"}
    resp = requests.post(qa_url, headers=headers, json=qa_payload)
    print_response("Create Q&A", qa_url, qa_payload, resp)
    qa_id = resp.json().get("id")
    resp = requests.get(qa_url, headers=headers)
    print_response("List Q&A", qa_url, None, resp)
    if qa_id:
        update_qa = {"question": "What is ML?", "answer": "Machine Learning", "language": "en"}
        qa_id_url = f"{qa_url}/{qa_id}"
        resp = requests.put(qa_id_url, headers=headers, json=update_qa)
        print_response("Update Q&A", qa_id_url, update_qa, resp)
        resp = requests.delete(qa_id_url, headers=headers)
        print_response("Delete Q&A", qa_id_url, None, resp)

    # Notes CRUD
    notes_url = f"{ADMIN_BASE_URL}/{app_id}/notes"
    note_payload = {"text": "This is a note.", "language": "en"}
    resp = requests.post(notes_url, headers=headers, json=note_payload)
    print_response("Create Note", notes_url, note_payload, resp)
    note_id = resp.json().get("id")
    resp = requests.get(notes_url, headers=headers)
    print_response("List Notes", notes_url, None, resp)
    if note_id:
        update_note = {"text": "Updated note.", "language": "en"}
        note_id_url = f"{notes_url}/{note_id}"
        resp = requests.put(note_id_url, headers=headers, json=update_note)
        print_response("Update Note", note_id_url, update_note, resp)
        resp = requests.delete(note_id_url, headers=headers)
        print_response("Delete Note", note_id_url, None, resp)

    # URLs CRUD
    urls_url = f"{ADMIN_BASE_URL}/{app_id}/urls"
    url_payload = {"url": "https://example.com", "description": "Example site", "language": "en"}
    resp = requests.post(urls_url, headers=headers, json=url_payload)
    print_response("Create URL", urls_url, url_payload, resp)
    url_id = resp.json().get("id")
    resp = requests.get(urls_url, headers=headers)
    print_response("List URLs", urls_url, None, resp)
    if url_id:
        update_url = {"url": "https://example.org", "description": "Updated site", "language": "en"}
        url_id_url = f"{urls_url}/{url_id}"
        resp = requests.put(url_id_url, headers=headers, json=update_url)
        print_response("Update URL", url_id_url, update_url, resp)
        resp = requests.delete(url_id_url, headers=headers)
        print_response("Delete URL", url_id_url, None, resp)

    # Documents CRUD
    docs_url = f"{ADMIN_BASE_URL}/{app_id}/documents"
    doc_payload = {"filename": "file.txt", "filetype": "text/plain", "url": "https://file.com", "language": "en"}
    resp = requests.post(docs_url, headers=headers, json=doc_payload)
    print_response("Create Document", docs_url, doc_payload, resp)
    doc_id = resp.json().get("id")
    resp = requests.get(docs_url, headers=headers)
    print_response("List Documents", docs_url, None, resp)
    if doc_id:
        update_doc = {"filename": "file2.txt", "filetype": "text/plain", "url": "https://file2.com", "language": "en"}
        doc_id_url = f"{docs_url}/{doc_id}"
        resp = requests.put(doc_id_url, headers=headers, json=update_doc)
        print_response("Update Document", doc_id_url, update_doc, resp)
        resp = requests.delete(doc_id_url, headers=headers)
        print_response("Delete Document", doc_id_url, None, resp)

    # Training/Re-indexing
    train_url = f"{ADMIN_BASE_URL}/{app_id}/train"
    resp = requests.post(train_url, headers=headers)
    print_response("Trigger Training/Re-indexing", train_url, None, resp)

    # Guardrails CRUD
    guardrails_url = f"{ADMIN_BASE_URL}/{app_id}/guardrails"
    guardrail_payload = {
        "ruleName": "No Spam",
        "ruleType": "blacklist_phrase",
        "pattern": "spam",
        "action": "block_input",
        "responseMessage": {"en": "No spam allowed."},
        "isActive": True
    }
    resp = requests.post(guardrails_url, headers=headers, json=guardrail_payload)
    print_response("Create Guardrail", guardrails_url, guardrail_payload, resp)
    guardrail_id = resp.json().get("id")
    resp = requests.get(guardrails_url, headers=headers)
    print_response("List Guardrails", guardrails_url, None, resp)
    if guardrail_id:
        update_guardrail = {
            "ruleName": "No Offensive Language",
            "ruleType": "blacklist_phrase",
            "pattern": "offensive",
            "action": "block_input",
            "responseMessage": {"en": "No offensive language allowed."},
            "isActive": True
        }
        guardrail_id_url = f"{guardrails_url}/{guardrail_id}"
        resp = requests.put(guardrail_id_url, headers=headers, json=update_guardrail)
        print_response("Update Guardrail", guardrail_id_url, update_guardrail, resp)
        resp = requests.delete(guardrail_id_url, headers=headers)
        print_response("Delete Guardrail", guardrail_id_url, None, resp)


def test_chat_flow(app_id):
    HEADERS = {"Content-Type": "application/json", "X-App-ID": app_id}
    session_id = None
    try:
        # 1. Initiate chat session (no session ID)
        payload = {"message": "Hello!"}
        response = requests.post(CHAT_BASE_URL, headers=HEADERS, json=payload)
        print_response("Initiate Chat Session", CHAT_BASE_URL, payload, response)
        data = response.json()
        session_id = data.get("sessionId") or data.get("session_id")
        assert session_id, "SessionId not returned!"
        time.sleep(1)

        # 2. Send normal message
        payload = {"message": "What can you do?"}
        headers = {**HEADERS, "X-Session-ID": session_id}
        response = requests.post(CHAT_BASE_URL, headers=headers, json=payload)
        print_response("Send Normal Message", CHAT_BASE_URL, payload, response)
        time.sleep(1)

        # 3. Send 'thank you' message
        payload = {"message": "Thank you!"}
        response = requests.post(CHAT_BASE_URL, headers=headers, json=payload)
        print_response("Send Thank You Message", CHAT_BASE_URL, payload, response)
        time.sleep(1)

        # 4. Switch language (e.g., to Spanish)
        payload = {"message": "Switch to Spanish"}
        response = requests.post(CHAT_BASE_URL, headers=headers, json=payload)
        print_response("Switch Language", CHAT_BASE_URL, payload, response)
        time.sleep(1)

        # 5. Send message in new language
        payload = {"message": "¿Qué puedes hacer?"}
        response = requests.post(CHAT_BASE_URL, headers=headers, json=payload)
        print_response("Message in New Language", CHAT_BASE_URL, payload, response)
        time.sleep(1)

        # 6. Trigger a guardrail (send blacklisted phrase)
        payload = {"message": "forbidden_phrase"}  # Replace with actual blacklisted phrase if you have one
        response = requests.post(CHAT_BASE_URL, headers=headers, json=payload)
        print_response("Trigger Guardrail", CHAT_BASE_URL, payload, response)
        time.sleep(1)

        # 7. Invalid AppId
        bad_headers = {**HEADERS, "X-App-ID": "invalid-app-id", "X-Session-ID": session_id}
        payload = {"message": "Hello!"}
        response = requests.post(CHAT_BASE_URL, headers=bad_headers, json=payload)
        print_response("Invalid AppId", CHAT_BASE_URL, payload, response)
        time.sleep(1)

        # 8. Invalid SessionId
        bad_headers = {**HEADERS, "X-Session-ID": "invalid-session-id"}
        payload = {"message": "Hello!"}
        response = requests.post(CHAT_BASE_URL, headers=bad_headers, json=payload)
        print_response("Invalid SessionId", CHAT_BASE_URL, payload, response)
        time.sleep(1)

        # 9. (Optional) Check chat history if endpoint exists
        # This step is a placeholder; implement if you have a chat history endpoint
        # print("Check chat history: Not implemented in this test.")
    except Exception as e:
        print(f"Exception during chat flow: {e}")


def main():
    app_id = create_app()
    if not app_id:
        print("App creation failed, aborting test.")
        return
    try:
        update_app_language(app_id, "en")
        test_admin_crud(app_id)
        test_chat_flow(app_id)
    finally:
        delete_app(app_id)

if __name__ == "__main__":
    main()
