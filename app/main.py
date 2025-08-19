# app/main.py
from fastapi import FastAPI
from .routers.admin import app as admin_app_router
from .routers import chat as chat_router

app = FastAPI(title="Chatbot Platform API")

# Routers
app.include_router(admin_app_router.router)
app.include_router(chat_router.router)

@app.get("/")
async def root():
    return {"message": "Chatbot API is running"}
