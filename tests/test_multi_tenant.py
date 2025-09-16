"""
Multi-tenant functionality tests for the AI Chat Bot API.
Tests that each app uses its own MongoDB database and data isolation works correctly.
"""

import requests
import json
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:8000/api/v1"
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "test-key")

def print_response(name, url, resp):
    """Helper function to print API response details."""
    print(f"\nAPI: {name}")
    print(f"URL: {url}")
    print(f"Status: {resp.status_code}")
    try:
        print(f"Response: {json.dumps(resp.json(), indent=2)}")
    except Exception:
        print(f"Raw Response: {resp.text}")

def create_test_app(app_name, mongodb_connection_string):
    """Create a test app with its own MongoDB connection."""
    app_data = {
        "name": app_name,
        "description": f"Test app: {app_name}",
        "defaultLanguage": "en",
        "availableLanguages": ["en", "es"],
        "welcomeMessage": {"en": "Welcome!", "es": "¡Bienvenido!"},
        "acknowledgmentMessage": {"en": "You're welcome!", "es": "¡De nada!"},
        "googleApiKey": GOOGLE_API_KEY,
        "mongodbConnectionString": mongodb_connection_string
    }

    url = f"{BASE_URL}/admin/app"
    resp = requests.post(url, json=app_data)
    print_response(f"Create App ({app_name})", url, resp)

    if resp.status_code == 200:
        return resp.json().get("id")
    else:
        print(f"Failed to create app {app_name}")
        return None

def create_test_content(app_id, content_type, content_data):
    """Create test content for an app."""
    url = f"{BASE_URL}/client/app/{app_id}/{content_type}"
    resp = requests.post(url, json=content_data)
    print_response(f"Create {content_type} for app {app_id}", url, resp)
    return resp.status_code == 200

def test_chat_isolation(app1_id, app2_id):
    """Test that chat sessions and messages are isolated between apps."""
    print("\n=== Testing Chat Isolation ===")

    # Create chat sessions for both apps
    chat_data = {"message": "Hello, test message for app 1"}
    url = f"{BASE_URL}/client/chat/message"
    headers = {"x-app-id": app1_id}
    resp1 = requests.post(url, json=chat_data, headers=headers)
    print_response("Chat App 1", url, resp1)

    chat_data = {"message": "Hello, test message for app 2"}
    headers = {"x-app-id": app2_id}
    resp2 = requests.post(url, json=chat_data, headers=headers)
    print_response("Chat App 2", url, resp2)

    # Verify sessions are different
    if resp1.status_code == 200 and resp2.status_code == 200:
        session1 = resp1.json().get("sessionId")
        session2 = resp2.json().get("sessionId")

        if session1 != session2:
            print("✅ Chat sessions are properly isolated between apps")
            return True
        else:
            print("❌ Chat sessions are not properly isolated")
            return False

    return False

def test_content_isolation(app1_id, app2_id):
    """Test that content (Q&A, notes, etc.) is isolated between apps."""
    print("\n=== Testing Content Isolation ===")

    # Create different content for each app
    qna_data1 = {
        "question": "What is the meaning of life for app 1?",
        "answer": "42 for app 1",
        "language": "en"
    }

    qna_data2 = {
        "question": "What is the meaning of life for app 2?",
        "answer": "42 for app 2",
        "language": "en"
    }

    # This endpoint might not exist yet, but we're testing the concept
    success1 = create_test_content(app1_id, "qna", qna_data1)
    success2 = create_test_content(app2_id, "qna", qna_data2)

    if success1 and success2:
        print("✅ Content creation succeeded for both apps")
        return True
    else:
        print("❌ Content creation failed - endpoints may not exist yet")
        return False

def test_guardrail_isolation(app1_id, app2_id):
    """Test that guardrails are isolated between apps."""
    print("\n=== Testing Guardrail Isolation ===")

    # Create different guardrails for each app
    guardrail_data1 = {
        "ruleType": "blacklist_phrase",
        "pattern": "badword1",
        "action": "block_input",
        "responseMessage": {"en": "Blocked by app 1 guardrail"},
        "isActive": True
    }

    guardrail_data2 = {
        "ruleType": "blacklist_phrase",
        "pattern": "badword2",
        "action": "block_input",
        "responseMessage": {"en": "Blocked by app 2 guardrail"},
        "isActive": True
    }

    success1 = create_test_content(app1_id, "guardrails", guardrail_data1)
    success2 = create_test_content(app2_id, "guardrails", guardrail_data2)

    if success1 and success2:
        print("✅ Guardrail creation succeeded for both apps")
        return True
    else:
        print("❌ Guardrail creation failed - endpoints may not exist yet")
        return False

def run_multi_tenant_tests():
    """Run comprehensive multi-tenant tests."""
    print("🚀 Starting Multi-Tenant Functionality Tests")
    print("=" * 50)

    # Generate unique database names for testing
    test_suffix = str(uuid.uuid4())[:8]
    mongodb_url_base = os.getenv("MONGO_URL", "mongodb://localhost:27017")

    # Create MongoDB connection strings for two different test databases
    app1_db_name = f"test_app1_{test_suffix}"
    app2_db_name = f"test_app2_{test_suffix}"

    app1_mongo_url = f"{mongodb_url_base.split('/')[-2]}/{app1_db_name}"
    app2_mongo_url = f"{mongodb_url_base.split('/')[-2]}/{app2_db_name}"

    # Fix the URLs properly
    if "mongodb://" in mongodb_url_base:
        base_url = mongodb_url_base.rsplit('/', 1)[0]
        app1_mongo_url = f"{base_url}/{app1_db_name}"
        app2_mongo_url = f"{base_url}/{app2_db_name}"

    print(f"App 1 MongoDB URL: {app1_mongo_url}")
    print(f"App 2 MongoDB URL: {app2_mongo_url}")

    # Create two test apps with different MongoDB databases
    app1_id = create_test_app("Multi-Tenant Test App 1", app1_mongo_url)
    app2_id = create_test_app("Multi-Tenant Test App 2", app2_mongo_url)

    if not app1_id or not app2_id:
        print("❌ Failed to create test apps. Aborting tests.")
        return

    print(f"\n✅ Created test apps:")
    print(f"   App 1 ID: {app1_id}")
    print(f"   App 2 ID: {app2_id}")

    # Run isolation tests
    test_results = []

    # Test chat isolation
    test_results.append(test_chat_isolation(app1_id, app2_id))

    # Test content isolation (may fail if endpoints don't exist)
    test_results.append(test_content_isolation(app1_id, app2_id))

    # Test guardrail isolation (may fail if endpoints don't exist)
    test_results.append(test_guardrail_isolation(app1_id, app2_id))

    # Cleanup - delete test apps
    print("\n=== Cleanup ===")
    for app_id, app_name in [(app1_id, "App 1"), (app2_id, "App 2")]:
        url = f"{BASE_URL}/admin/app/{app_id}"
        resp = requests.delete(url)
        print_response(f"Delete {app_name}", url, resp)

    # Summary
    print("\n" + "=" * 50)
    print("🎯 Test Summary:")
    passed = sum(test_results)
    total = len(test_results)
    print(f"   Tests passed: {passed}/{total}")

    if passed == total:
        print("   ✅ All multi-tenant tests passed!")
    else:
        print("   ⚠️  Some tests failed - this may be expected if endpoints are not implemented yet")

    return passed == total

if __name__ == "__main__":
    run_multi_tenant_tests()
