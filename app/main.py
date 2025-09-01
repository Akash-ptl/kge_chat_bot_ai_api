# app/main.py

from fastapi import FastAPI
from contextlib import asynccontextmanager
from .routers.admin import app as admin_app_router
from .routers.admin import qna as admin_qna_router
from .routers.admin import notes as admin_notes_router
from .routers.admin import urls as admin_urls_router
from .routers.admin import documents as admin_documents_router
from .routers.admin import guardrail as admin_guardrail_router
from .routers.admin import reindex as admin_train_router
from .routers.admin import settings as admin_settings_router
from .routers import chat as chat_router


# Lifespan context to ensure async resources are managed for testing
@asynccontextmanager
async def lifespan(app):
    yield

app = FastAPI(title="Chatbot Platform API", lifespan=lifespan)

# Routers
import logging
logging.basicConfig(level=logging.INFO)
app.include_router(admin_app_router.router)
app.include_router(admin_qna_router.router)
app.include_router(admin_notes_router.router)
app.include_router(admin_urls_router.router)
app.include_router(admin_documents_router.router)
app.include_router(admin_guardrail_router.router)
app.include_router(admin_train_router.router)
app.include_router(admin_settings_router.router)
app.include_router(chat_router.router)

@app.get("/")
async def root():
    return {"message": "Chatbot API is running"}




# AIzaSyDVm1IWybAQwb-AtcxwXWd3R5Oww4ZhOkc

# AIzaSyDKzpg3Z8aLmY_lIoXRu7svHpDafmT_DhI

# /Users/akashptl/Cli/KGE/Chat_Bot/ai_chat_bot/.venv/bin/python tests/test_api_crud.py
