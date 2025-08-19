# app/main.py

from fastapi import FastAPI
from .routers.admin import app as admin_app_router
from .routers.admin import qna as admin_qna_router
from .routers.admin import notes as admin_notes_router
from .routers.admin import urls as admin_urls_router
from .routers.admin import documents as admin_documents_router
from .routers.admin import guardrail as admin_guardrail_router
from .routers.admin import reindex as admin_reindex_router

app = FastAPI(title="Chatbot Platform API")

# Routers
app.include_router(admin_app_router.router)
app.include_router(admin_qna_router.router)
app.include_router(admin_notes_router.router)
app.include_router(admin_urls_router.router)
app.include_router(admin_documents_router.router)
app.include_router(admin_guardrail_router.router)
app.include_router(admin_reindex_router.router)

@app.get("/")
async def root():
    return {"message": "Chatbot API is running"}
