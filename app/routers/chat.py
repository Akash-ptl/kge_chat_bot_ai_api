# app/routers/chat.py
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/chat", tags=["Chat User"])

@router.post("/message")
async def send_message():
    return {"message": "Chat endpoint placeholder. Logic to be implemented."}
