from fastapi import APIRouter, HTTPException, Query, File, UploadFile
from uuid import uuid4
from datetime import datetime, timedelta
from app.utils.db import db_instance
from app.setup_rollbar import rollbar_handler
from app.models.chat import CreateChat, SendMessage

router = APIRouter()

@router.post("/upload_story")
@rollbar_handler
async def upload_story(isu: int, file: UploadFile = File(...)):
    user_collection = db_instance.get_collection("users")
    stories_collection = db_instance.get_collection("stories")
    
    file_extension = file.filename.split(".")[-1]
    filename = f"stories/{isu}_{uuid4()}.{file_extension}"
    
    curr_time = datetime.now()
    expiration = curr_time + timedelta(hours=24)
    expiration_date = int(expiration.timestamp())
    
    file_url = db_instance.upload_file_to_minio(
        file.file,
        filename,
        content_type=file.content_type or "application/octet-stream",
    )
    update_result = await stories_collection.update_one(
        {"isu": isu},
        {"url": file_url},
        {"expiration_date": expiration_date}
    )
    
    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Story cannot be inserted")
    
    return {"expDate": expiration_date, "id": update_result.updated_id}

    