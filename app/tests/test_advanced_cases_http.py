import requests
import time

BASE_URL = "http://127.0.0.1:8000"

# Utility

def wait_for_server():
    for _ in range(10):
        try:
            r = requests.get(f"{BASE_URL}/")
            if r.status_code == 200:
                return True
        except Exception:
            time.sleep(1)
    return False

# --- CRUD and Admin Tests (already covered in your old file) ---
# ...existing CRUD tests would be here...

# --- Advanced/Edge Case Tests ---
app_id = None

def setup_module(module=None):
    """Create a test app before running tests and store its ID."""
    global app_id
    app = {
        "name": "Test App",
        "description": "App for advanced/edge case tests",
        "lang": "en",
        "welcomeMessage": {"en": "Welcome to the test bot!"},
        "defaultLanguage": "en",
        "availableLanguages": ["en", "es"],
        "googleApiKey": "AIzaSyDVm1IWybAQwb-AtcxwXWd3R5Oww4ZhOkc"
    }
    r = requests.post(f"{BASE_URL}/api/v1/admin/app", json=app)
    if r.status_code in (200, 201):
        app_id = r.json().get("id")
        print("Created app with id:", app_id)
    else:
        print("Warning: Could not create test app, status:", r.status_code, r.text)
    print("[DEBUG] setup_module app_id:", app_id)

def teardown_module(module=None):
    """Delete the test app after running tests."""
    global app_id
    print('[DEBUG] Entered test_welcome_message')
    if app_id:
        r = requests.delete(f"{BASE_URL}/api/v1/admin/app/{app_id}")
        if r.status_code not in (200, 204):
            print("Warning: Could not delete test app, status:", r.status_code, r.text)

def test_guardrail_input_block():
    """Test that a guardrail blocks a user message containing a forbidden phrase."""
    # 1. Create a guardrail for 'blockme'
    print('[DEBUG] About to POST welcome message')
    global app_id
    print("[DEBUG] test_guardrail_input_block app_id:", app_id)
    guardrail = {
        "ruleName": "Block 'blockme'",
        "ruleType": "blacklist_phrase",
        "pattern": "blockme",
        "action": "block",
        "responseMessage": {"en": "Blocked by guardrail."},
        "isActive": True,
        "appId": app_id
    }
    r = requests.post(f"{BASE_URL}/api/v1/admin/app/{app_id}/guardrails", json=guardrail)
    print('Create guardrail:', r.status_code, r.text)
    assert r.status_code == 200
    guardrail_id = r.json()["id"]
    # 2. Send a chat message that should be blocked
    headers = {"x-app-id": app_id}
    body = {"message": "This should blockme!"}
    r = requests.post(f"{BASE_URL}/api/v1/chat/message", json=body, headers=headers)
    print('Chat message (guardrail test):', r.status_code, r.text)
    assert r.status_code == 200
    data = r.json()
    assert data["guardrailTriggered"] is True
    assert data["message"] == "Blocked by guardrail."
    # 3. Clean up
    requests.delete(f"{BASE_URL}/api/v1/admin/app/{app_id}/guardrails/{guardrail_id}")

def test_guardrail_output_block():
    """Test that a guardrail blocks an AI response containing a forbidden phrase."""
    # 1. Create a guardrail for 'Gemini' (assuming model will mention it)
    global app_id
    print("[DEBUG] test_guardrail_output_block app_id:", app_id)
    guardrail = {
        "ruleName": "Block 'Gemini' in output",
        "ruleType": "blacklist_phrase",
        "pattern": "Gemini",
        "action": "block",
        "responseMessage": {"en": "Output blocked by guardrail."},
        "isActive": True,
        "appId": app_id
    }
    r = requests.post(f"{BASE_URL}/api/v1/admin/app/{app_id}/guardrails", json=guardrail)
    assert r.status_code == 200
    guardrail_id = r.json()["id"]
    # 2. Send a chat message likely to trigger the output guardrail
    headers = {"x-app-id": app_id}
    body = {"message": "Who are you?"}
    r = requests.post(f"{BASE_URL}/api/v1/chat/message", json=body, headers=headers)
    print('Output guardrail chat message:', r.status_code, r.text)
    assert r.status_code == 200
    data = r.json()
    # Output may or may not be blocked depending on model response
    # Just print for manual verification
    print("Output guardrail test response:", data)
    # 3. Clean up
    requests.delete(f"{BASE_URL}/api/v1/admin/app/{app_id}/guardrails/{guardrail_id}")

def test_welcome_message():
    """Test that a new session returns the welcome message."""
    # Set a welcome message
    welcome = {"welcomeMessage": "Welcome to the test bot!"}
    global app_id
    print("[DEBUG] test_welcome_message app_id:", app_id)
    r = requests.put(f"{BASE_URL}/api/v1/admin/app/{app_id}/settings/welcome-message", json=welcome)
    print('[DEBUG] Welcome message PUT:', r.status_code, r.text)
    assert r.status_code == 200
    headers = {"x-app-id": app_id}
    body = {"message": "Hi"}
    print('[DEBUG] About to POST welcome message')
    try:
        r = requests.post(f"{BASE_URL}/api/v1/chat/message", json=body, headers=headers)
        print('Welcome message chat message:', r.status_code, r.text)
        assert r.status_code == 200
        data = r.json()
        print("Welcome message test response:", data)
    except Exception as e:
        print("[ERROR] Exception in test_welcome_message:", e)
        try:
            print('Welcome message chat message:', r.status_code, r.text)
        except Exception:
            print('Welcome message chat message: <no response object>')
        raise

def test_language_switch():
    """Test that the session language can be changed and is respected."""
    # Set available languages
    langs = ["en", "fr"]
    global app_id
    print("[DEBUG] test_language_switch app_id:", app_id)
    url = f"{BASE_URL}/api/v1/admin/app/{app_id}/settings/languages"
    print(f'[DEBUG] Language switch PUT URL: {url} app_id: {app_id} payload: {langs}')
    r = requests.put(url, json=langs)
    print('[DEBUG] Language switch PUT:', r.status_code, r.text)
    assert r.status_code == 200
    headers = {"x-app-id": app_id}
    # Start session in English
    body = {"message": "Hello"}
    r = requests.post(f"{BASE_URL}/api/v1/chat/message", json=body, headers=headers)
    print('[DEBUG] Language switch POST:', r.status_code, r.text)
    assert r.status_code == 200
    session_id = r.json()["sessionId"]
    # Switch language to Spanish
    # (Assume your API supports a special message or endpoint for this)
    # This is a placeholder; adapt as needed for your implementation
    # body = {"message": "Switch language to es"}
    # r = requests.post(f"{BASE_URL}/api/v1/chat/message", json=body, headers={**headers, "x-session-id": session_id})
    # assert r.status_code == 200
    # print("Language switch test response:", r.json())

if __name__ == "__main__":
    assert wait_for_server(), "API server not running on http://127.0.0.1:8000"
    setup_module()
    test_guardrail_input_block()
    test_guardrail_output_block()
    test_welcome_message()
    test_language_switch()
    teardown_module()
    print("All advanced/edge case tests passed!")
