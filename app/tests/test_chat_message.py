import requests
import time

BASE_URL = "http://127.0.0.1:8001"

def wait_for_server():
    for _ in range(10):
        try:
            r = requests.get(f"{BASE_URL}/")
            if r.status_code == 200:
                return True
        except Exception:
            time.sleep(1)
    return False

def test_chat_message():
    # Assumes test_app exists and has a googleApiKey set
    headers = {"X-App-ID": "test_app"}
    data = {"message": "Hello, bot!"}
    r = requests.post(f"{BASE_URL}/api/v1/chat/message", json=data, headers=headers)
    assert r.status_code == 200
    resp = r.json()
    assert "sessionId" in resp
    assert "message" in resp
    assert resp["message"]

if __name__ == "__main__":
    assert wait_for_server(), "API server not running on http://127.0.0.1:8001"
    test_chat_message()
    print("Chat endpoint test passed!")
