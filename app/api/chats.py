from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from uuid import uuid4
from bson import ObjectId
from datetime import timedelta

from app.utils.db import db_instance
from app.setup_rollbar import rollbar_handler
from app.models.chat import CreateChat, SendMessage
from app.utils.serializer import serialize

router = APIRouter()


@router.post("/create_chat")
@rollbar_handler
async def create_chat(payload: CreateChat):
    if payload.isu_1 == payload.isu_2:
        raise HTTPException(status_code=400, detail="chat cannot be created for the same user")

    chat_id = str(uuid4())
    await db_instance.create_chat(chat_id=chat_id, isu_1=payload.isu_1, isu_2=payload.isu_2)
    return {"chat_id": chat_id}


@router.get("/user_chats/{isu}")
@rollbar_handler
async def get_chats_for_user(isu: int):
    chats = await db_instance.get_chats_by_user(isu)
    if not chats:
        return {"chats": []}

    # Serialize all ObjectId fields to strings
    serialized_chats = [serialize(chat) for chat in chats]

    return {"chats": serialized_chats}


@router.post("/send_message")
@rollbar_handler
async def send_message(payload: SendMessage):
    message_id = await db_instance.create_message(
        chat_id=payload.chat_id,
        sender_id=payload.sender_id,
        receiver_id=payload.receiver_id,
        text=payload.text,
    )
    return {"message_id": message_id}


@router.get("/get_messages/{chat_id}")
@rollbar_handler
async def get_messages(chat_id: str, limit: int = Query(5, gt=0), offset: int = Query(0, ge=0)):
    messages = await db_instance.get_messages(chat_id=chat_id, limit=limit, offset=offset)
    if not messages:
        return {"messages": []}

    formatted_messages = []
    for message in messages:
        formatted_message = {
            "chat_id": message["chat_id"],
            "message_id": message["message_id"],
            "sender_id": message["sender_id"],
            "receiver_id": message["receiver_id"],
            "timestamp": message["timestamp"],
        }
        if "media_id" in message and message["media_id"]:
            formatted_message["media_id"] = message["media_id"]
        else:
            formatted_message["text"] = message.get("text", "")

        formatted_messages.append(formatted_message)

    return {"messages": formatted_messages}


@router.post("/upload_media")
@rollbar_handler
async def upload_media(isu: int, chat_id: str, file: UploadFile = File(...)):
    file_extension = file.filename.split(".")[-1]
    filename = f"media/{chat_id}/{isu}_{uuid4()}.{file_extension}"

    file_url = db_instance.upload_file_to_minio(
        file.file,
        filename,
        content_type=file.content_type or "application/octet-stream",
    )

    media_id = await db_instance.save_media(isu, chat_id, file_url)

    return {"media_id": media_id}


@router.get("/get_media")
@rollbar_handler
async def get_media(media_id: str):
    media_collection = db_instance.get_collection("media")
    media = await media_collection.find_one({"_id": ObjectId(media_id)})

    path = media["path"]
    bucket_prefix = f"{db_instance.minio_bucket_name}/"
    if path.startswith(bucket_prefix):
        path = path[len(bucket_prefix) :]

    presigned_url = db_instance.generate_presigned_url(object_name=path, expiration=timedelta(hours=3))

    return {
        "media_id": str(media["_id"]),
        "isu": media["isu"],
        "chat_id": media["chat_id"],
        "url": presigned_url,
        "created_at": media["created_at"],
    }
