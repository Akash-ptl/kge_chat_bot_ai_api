# app/main.py

from fastapi import FastAPI
from contextlib import asynccontextmanager
from .routers.admin import app as client_app_router
from .routers.admin import qna as client_qna_router
from .routers.admin import notes as client_notes_router
from .routers.admin import urls as client_urls_router
from .routers.admin import documents as client_documents_router
from .routers.admin import guardrail as client_guardrail_router
# from .routers.admin import reindex as client_train_router  # Commented out train model API
from .routers.admin import settings as client_settings_router
from .routers import chat as chat_router


# Lifespan context to ensure async resources are managed for testing
@asynccontextmanager
async def lifespan(app):
    yield

app = FastAPI(title="Chatbot Platform API", lifespan=lifespan)

# Routers
import logging
logging.basicConfig(level=logging.INFO)
app.include_router(client_app_router.router)
app.include_router(client_qna_router.router)
app.include_router(client_notes_router.router)
app.include_router(client_urls_router.router)
app.include_router(client_documents_router.router)
app.include_router(client_guardrail_router.router)
# app.include_router(client_train_router.router)  # Commented out train model API
app.include_router(client_settings_router.router)
app.include_router(chat_router.router)

@app.get("/")
def root():
    return {"message": "Chatbot API is running"}



# /Users/akashptl/Cli/KGE/Chat_Bot/ai_chat_bot/.venv/bin/uvicorn app.main:app --port 8000 --reload


