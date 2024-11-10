from fastapi import APIRouter, HTTPException, Query
from uuid import uuid4

from app.utils.db import db_instance
from app.setup_rollbar import rollbar_handler
from app.models.chat import CreateChat, SendMessage

router = APIRouter()

@router.post("/create_chat")
@rollbar_handler
async def create_chat(payload: CreateChat):
    if payload.isu_1 == payload.isu_2:
        raise HTTPException(status_code=400, detail="Chat cannot be created for the same user")

    chat_id = str(uuid4())
    await db_instance.create_chat(chat_id=chat_id, isu_1=payload.isu_1, isu_2=payload.isu_2)
    return {"message": "Chat created", "chat_id": chat_id}

@router.get("/user_chats/{isu}")
@rollbar_handler
async def get_chats_for_user(isu: int):
    chats = await db_instance.get_chats_by_user(isu)
    if not chats:
        raise HTTPException(status_code=404, detail="chats not found for this user")
    
    return {"chats": chats}

@router.post("/send_message", response_model=dict)
@rollbar_handler
async def send_message(payload: SendMessage):
    message_id = await db_instance.create_message(
        chat_id=payload.chat_id,
        sender_id=payload.sender_id,
        receiver_id=payload.receiver_id,
        text=payload.text
    )
    return {"message": "message sent", "message_id": message_id}

@router.get("/get_messages/{chat_id}")
@rollbar_handler
async def get_messages(chat_id: str, limit: int = Query(5, gt=0), offset: int = Query(0, ge=0)):
    messages = await db_instance.get_messages(chat_id=chat_id, limit=limit, offset=offset)
    if not messages:
        raise HTTPException(status_code=404, detail="messages not found")
    return {"messages": messages}