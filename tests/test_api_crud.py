
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def print_response(name, url, resp):
    print(f"\nAPI: {name}")
    print(f"URL: {url}")
    print(f"Status: {resp.status_code}")
    try:
        print(f"Response: {json.dumps(resp.json(), indent=2)}")
    except Exception:
        print(f"Raw Response: {resp.text}")

def run_api_tests():
    # 1. Create App
    import os
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "test-key")
    app_data = {
        "name": "Test App",
        "description": "A test app.",
        "defaultLanguage": "en",
        "availableLanguages": ["en", "es"],
        "welcomeMessage": {"en": "Welcome!", "es": "¡Bienvenido!"},
        "acknowledgmentMessage": {"en": "You're welcome!", "es": "¡De nada!"},
    "googleApiKey": GOOGLE_API_KEY
    }
    url = f"{BASE_URL}/admin/app"
    resp = requests.post(url, json=app_data)
    print_response("Create App", url, resp)
    app_id = resp.json().get("id")
    if not app_id:
        print("App creation failed, aborting test.")
        return

    # 2. App CRUD
    url = f"{BASE_URL}/admin/app/{app_id}"
    resp = requests.get(url)
    print_response("Get App", url, resp)

    update_data = {
        "name": "Updated App",
        "description": "Updated description.",
        "defaultLanguage": "es",
        "availableLanguages": ["en", "es", "fr"],
        "welcomeMessage": {"en": "Welcome!", "es": "¡Bienvenido!", "fr": "Bienvenue!"},
        "acknowledgmentMessage": {"en": "You're welcome!", "es": "¡De nada!", "fr": "De rien!"},
    "googleApiKey": GOOGLE_API_KEY
    }
    resp = requests.put(url, json=update_data)
    print_response("Update App", url, resp)

    # 3. Notes CRUD
    note_data = {"text": "Test note", "language": "en"}
    url = f"{BASE_URL}/admin/app/{app_id}/notes"
    resp = requests.post(url, json=note_data)
    print_response("Create Note", url, resp)
    note_id = resp.json().get("id")

    resp = requests.get(url)
    print_response("List Notes", url, resp)

    if note_id:
        update_note = {"text": "Updated note", "language": "en"}
        url_note = f"{BASE_URL}/admin/app/{app_id}/notes/{note_id}"
        resp = requests.put(url_note, json=update_note)
        print_response("Update Note", url_note, resp)
        resp = requests.delete(url_note)
        print_response("Delete Note", url_note, resp)

    # 4. URLs CRUD
    url_data = {"url": "https://example.com", "description": "desc", "language": "en"}
    url_urls = f"{BASE_URL}/admin/app/{app_id}/urls"
    resp = requests.post(url_urls, json=url_data)
    print_response("Create URL", url_urls, resp)
    url_id = resp.json().get("id")

    resp = requests.get(url_urls)
    print_response("List URLs", url_urls, resp)

    if url_id:
        update_url = {"url": "https://updated.com", "description": "desc2", "language": "en"}
        url_url = f"{BASE_URL}/admin/app/{app_id}/urls/{url_id}"
        resp = requests.put(url_url, json=update_url)
        print_response("Update URL", url_url, resp)
        resp = requests.delete(url_url)
        print_response("Delete URL", url_url, resp)

    # 5. Guardrails CRUD
    guardrail_data = {
        "appId": app_id,
        "ruleName": "Block offensive language",
        "ruleType": "blacklist_phrase",
        "pattern": "badword",
        "action": "block",
        "responseMessage": {"en": "Your message was blocked.", "es": "Su mensaje fue bloqueado."},
        "isActive": True
    }
    url_guardrails = f"{BASE_URL}/admin/app/{app_id}/guardrails"
    resp = requests.post(url_guardrails, json=guardrail_data)
    print_response("Create Guardrail", url_guardrails, resp)
    guardrail_id = resp.json().get("id")

    resp = requests.get(url_guardrails)
    print_response("List Guardrails", url_guardrails, resp)

    if guardrail_id:
        update_guardrail = {
            "appId": app_id,
            "ruleName": "Block offensive language updated",
            "ruleType": "blacklist_phrase",
            "pattern": "badword2",
            "action": "warn",
            "responseMessage": {"en": "Warning!", "es": "¡Advertencia!"},
            "isActive": False
        }
        url_guard = f"{BASE_URL}/admin/app/{app_id}/guardrails/{guardrail_id}"
        resp = requests.put(url_guard, json=update_guardrail)
        print_response("Update Guardrail", url_guard, resp)
        resp = requests.delete(url_guard)
        print_response("Delete Guardrail", url_guard, resp)

    # 6. QnA CRUD
    qna_data = {"question": "What is AI?", "answer": "Artificial Intelligence", "language": "en"}
    url_qna = f"{BASE_URL}/admin/app/{app_id}/qna"
    resp = requests.post(url_qna, json=qna_data)
    print_response("Create QnA", url_qna, resp)
    qna_id = resp.json().get("id")

    resp = requests.get(url_qna)
    print_response("List QnA", url_qna, resp)

    if qna_id:
        update_qna = {"question": "What is ML?", "answer": "Machine Learning", "language": "en"}
        url_q = f"{BASE_URL}/admin/app/{app_id}/qna/{qna_id}"
        resp = requests.put(url_q, json=update_qna)
        print_response("Update QnA", url_q, resp)
        resp = requests.delete(url_q)
        print_response("Delete QnA", url_q, resp)

    # 7. Documents CRUD
    doc_data = {"filename": "file.txt", "filetype": "text/plain", "url": "https://file.com", "language": "en"}
    url_docs = f"{BASE_URL}/admin/app/{app_id}/documents"
    resp = requests.post(url_docs, json=doc_data)
    print_response("Create Document", url_docs, resp)
    doc_id = resp.json().get("id")

    resp = requests.get(url_docs)
    print_response("List Documents", url_docs, resp)

    if doc_id:
        update_doc = {"filename": "file2.txt", "filetype": "text/plain", "url": "https://file2.com", "language": "en"}
        url_doc = f"{BASE_URL}/admin/app/{app_id}/documents/{doc_id}"
        resp = requests.put(url_doc, json=update_doc)
        print_response("Update Document", url_doc, resp)
        resp = requests.delete(url_doc)
        print_response("Delete Document", url_doc, resp)

    # 8. Settings
    url_settings = f"{BASE_URL}/admin/app/{app_id}/settings"
    url_welcome = f"{url_settings}/welcome-message"
    welcome_data = {"en": "Hello!", "es": "¡Hola!"}
    resp = requests.put(url_welcome, json=welcome_data)
    print_response("Update Welcome Message", url_welcome, resp)

    url_lang = f"{url_settings}/languages-settings"
    lang_data = {"availableLanguages": ["en", "fr"], "defaultLanguage": "fr"}
    resp = requests.put(url_lang, json=lang_data)
    print_response("Update Languages Settings", url_lang, resp)

    url_google = f"{url_settings}/google-api-key"
    resp = requests.put(url_google, json=GOOGLE_API_KEY)
    print_response("Update Google API Key", url_google, resp)

    # 9. Train
    url_train = f"{BASE_URL}/admin/app/{app_id}/train"
    resp = requests.post(url_train)
    print_response("Trigger Train", url_train, resp)

    # 10. Chat
    url_chat = f"{BASE_URL}/chat/message"
    chat_data = {"message": "Hello!"}
    headers = {"x-app-id": app_id}
    resp = requests.post(url_chat, json=chat_data, headers=headers)
    print_response("Chat Message", url_chat, resp)

    # 11. Delete App
    url = f"{BASE_URL}/admin/app/{app_id}"
    resp = requests.delete(url)
    print_response("Delete App", url, resp)

if __name__ == "__main__":
    run_api_tests()
