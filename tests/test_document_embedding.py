import requests
import json
import time

ADMIN_BASE_URL = "http://localhost:8000/api/v1/admin/app"
DOCS_URL_TEMPLATE = ADMIN_BASE_URL + "/{app_id}/documents"
CHAT_BASE_URL = "http://localhost:8000/api/v1/chat/message"
import os
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "test-key")
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
        headers = {"Content-Type": "application/json", "X-App-ID": app_id}
        session_id = None

        # Multiple Q&A (unique, paraphrased, and hard)
        qnas = [
            {"question": "What is FastAPI?", "answer": "FastAPI is a modern, fast web framework for building APIs with Python.", "language": "en"},
            {"question": "What is Python?", "answer": "Python is a popular programming language.", "language": "en"}
        ]
        qna_url = f"{ADMIN_BASE_URL}/{app_id}/qna"
        for qna in qnas:
            resp = requests.post(qna_url, json=qna)
            print_response("Create QnA", qna_url, qna, resp)
        time.sleep(1)

        # Multiple Notes (unique, paraphrased, and hard)
        notes = [
            {"text": "This is a note about the chatbot system.", "language": "en"},
            {"text": "This is a second note about AI chatbots.", "language": "en"}
        ]
        note_url = f"{ADMIN_BASE_URL}/{app_id}/notes"
        for note in notes:
            resp = requests.post(note_url, json=note)
            print_response("Create Note", note_url, note, resp)
        time.sleep(1)

        # Multiple URLs (unique, paraphrased, and hard)
        urls = [
            {"url": "https://fastapi.tiangolo.com/", "description": "Official FastAPI documentation", "language": "en"},
            {"url": "https://www.python.org/", "description": "Official Python website", "language": "en"}
        ]
        url_url = f"{ADMIN_BASE_URL}/{app_id}/urls"
        for url in urls:
            resp = requests.post(url_url, json=url)
            print_response("Create URL", url_url, url, resp)
        time.sleep(1)

        # Multiple PDFs
        pdf_urls = [
            "https://www.adobe.com/support/products/enterprise/knowledgecenter/media/c4611_sample_explain.pdf",
            "https://s24.q4cdn.com/216390268/files/doc_downloads/test.pdf"
        ]
        for pdf_url in pdf_urls:
            doc_payload = {
                "filename": pdf_url.split("/")[-1],
                "filetype": "application/pdf",
                "url": pdf_url,
                "language": "en"
            }
            docs_url = f"{ADMIN_BASE_URL}/{app_id}/documents"
            resp = requests.post(docs_url, headers=headers, json=doc_payload)
            print_response("Upload PDF Document", docs_url, doc_payload, resp)
        time.sleep(3)


        # Start chat session and ask about each QnA, Note, URL, and PDF with paraphrased/hard queries
        # QnA
        payload = {"message": "Can you explain the main features of FastAPI?"}
        resp_chat = requests.post(CHAT_BASE_URL, headers=headers, json=payload)
        print_response("Ask QnA1 in Chat (paraphrased)", CHAT_BASE_URL, payload, resp_chat)
        try:
            session_id = resp_chat.json().get("sessionId")
        except Exception:
            session_id = None
        if session_id:
            headers["X-Session-Id"] = session_id
        payload2 = {"message": "Tell me about the programming language called Python."}
        resp_chat2 = requests.post(CHAT_BASE_URL, headers=headers, json=payload2)
        print_response("Ask QnA2 in Chat (paraphrased)", CHAT_BASE_URL, payload2, resp_chat2)

        # Notes
        payload3 = {"message": "Summarize the note related to the chatbot system."}
        resp_chat3 = requests.post(CHAT_BASE_URL, headers=headers, json=payload3)
        print_response("Ask Note1 in Chat (paraphrased)", CHAT_BASE_URL, payload3, resp_chat3)
        payload4 = {"message": "What does the second note about AI chatbots say?"}
        resp_chat4 = requests.post(CHAT_BASE_URL, headers=headers, json=payload4)
        print_response("Ask Note2 in Chat (paraphrased)", CHAT_BASE_URL, payload4, resp_chat4)

        # URLs
        payload5 = {"message": "Where can I find the official documentation for FastAPI?"}
        resp_chat5 = requests.post(CHAT_BASE_URL, headers=headers, json=payload5)
        print_response("Ask URL1 in Chat (paraphrased)", CHAT_BASE_URL, payload5, resp_chat5)
        payload6 = {"message": "Give me the main website for Python programming."}
        resp_chat6 = requests.post(CHAT_BASE_URL, headers=headers, json=payload6)
        print_response("Ask URL2 in Chat (paraphrased)", CHAT_BASE_URL, payload6, resp_chat6)

        # PDFs
        payload7 = {"message": "What is Features Demonstrated in pdf?"}
        resp_chat7 = requests.post(CHAT_BASE_URL, headers=headers, json=payload7)
        print_response("Ask PDF1 in Chat", CHAT_BASE_URL, payload7, resp_chat7)
        payload8 = {"message": "What is in the PDF document?"}
        resp_chat8 = requests.post(CHAT_BASE_URL, headers=headers, json=payload8)
        print_response("Ask PDF2 in Chat", CHAT_BASE_URL, payload8, resp_chat8)
    finally:
        delete_app(app_id)

if __name__ == "__main__":
    main()
