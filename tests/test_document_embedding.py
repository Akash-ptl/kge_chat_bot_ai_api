import requests
import json
import time

ADMIN_BASE_URL = "http://localhost:8000/api/v1/admin/app"
DOCS_URL_TEMPLATE = ADMIN_BASE_URL + "/{app_id}/documents"
CHAT_BASE_URL = "http://localhost:8000/api/v1/chat/message"
GOOGLE_API_KEY = "AIzaSyDVm1IWybAQwb-AtcxwXWd3R5Oww4ZhOkc"  # Use your real key if needed
PDF_URL = "https://www.adobe.com/support/products/enterprise/knowledgecenter/media/c4611_sample_explain.pdf"


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
        "name": "Doc Embedding Test App",
        "description": "App for document embedding test.",
        "defaultLanguage": "en",
        "availableLanguages": ["en", "es"],
        "welcomeMessage": {"en": "Welcome!", "es": "¡Bienvenido!"},
        "acknowledgmentMessage": {"en": "You're welcome!", "es": "¡De nada!"},
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

def delete_app(app_id):
    url = f"{ADMIN_BASE_URL}/{app_id}"
    resp = requests.delete(url)
    print(f"Delete App: {resp.status_code}")
    try:
        print(resp.json())
    except Exception:
        print(resp.text)

def upload_pdf(app_id):
    docs_url = DOCS_URL_TEMPLATE.format(app_id=app_id)
    doc_payload = {
        "filename": "pdf-test.pdf",
        "filetype": "application/pdf",
        "url": PDF_URL,
        "language": "en"
    }
    headers = {"Content-Type": "application/json", "X-App-ID": app_id}
    resp = requests.post(docs_url, headers=headers, json=doc_payload)
    print_response("Upload PDF Document", docs_url, doc_payload, resp)
    return resp.json().get("id")

def ask_about_pdf(app_id):
    headers = {"Content-Type": "application/json", "X-App-ID": app_id}
    payload = {"message": "What is in the PDF document?"}
    resp = requests.post(CHAT_BASE_URL, headers=headers, json=payload)
    print_response("Ask About PDF Document (first)", CHAT_BASE_URL, payload, resp)
    # If sessionId is returned, send a follow-up message in the same session
    try:
        session_id = resp.json().get("sessionId")
    except Exception:
        session_id = None
    if session_id:
        headers["X-Session-Id"] = session_id
        payload2 = {"message": "What is Features Demonstrated in pdf?"}
        resp2 = requests.post(CHAT_BASE_URL, headers=headers, json=payload2)
        print_response("Ask About PDF Document (follow-up)", CHAT_BASE_URL, payload2, resp2)
        return resp2
    return resp

def main():
    app_id = create_app()
    if not app_id:
        print("App creation failed, aborting test.")
        return
    try:
        doc_id = upload_pdf(app_id)
        time.sleep(3)  # Wait for embedding/indexing
        ask_about_pdf(app_id)
    finally:
        delete_app(app_id)

if __name__ == "__main__":
    main()
