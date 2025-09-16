from dotenv import load_dotenv
load_dotenv()

import requests
import json
import os

BASE_URL = "http://localhost:8000/api/v1"

def create_valid_app():
    """Create a valid app with all required fields including MongoDB connection string."""

    # Get environment variables
    google_api_key = os.getenv("GOOGLE_API_KEY", "test-key")
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")

    # Create MongoDB connection string for the app (using a separate database)
    app_mongo_url = f"{mongo_url.rsplit('/', 1)[0]}/sample_app_db"

    app_data = {
        "name": "Sample Chat Bot App",
        "description": "A sample chatbot application for testing",
        "defaultLanguage": "en",
        "availableLanguages": ["en", "es", "fr"],
        "welcomeMessage": {
            "en": "Welcome to our chatbot!",
            "es": "¡Bienvenido a nuestro chatbot!",
            "fr": "Bienvenue dans notre chatbot!"
        },
        "acknowledgmentMessage": {
            "en": "You're welcome!",
            "es": "¡De nada!",
            "fr": "De rien!"
        },
        "googleApiKey": google_api_key,
        "mongodbConnectionString": app_mongo_url
    }

    print("Creating app with data:")
    print(json.dumps(app_data, indent=2))

    url = f"{BASE_URL}/admin/app"
    response = requests.post(url, json=app_data)

    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Body: {response.text}")

    if response.status_code == 200:
        app_id = response.json().get("id")
        print(f"\n✅ Successfully created app with ID: {app_id}")
        return app_id
    else:
        print("❌ Failed to create app")
        return None

if __name__ == "__main__":
    create_valid_app()
