from fastapi import APIRouter, HTTPException, File, UploadFile
from uuid import uuid4
from datetime import datetime, timedelta
from app.utils.db import db_instance
from app.setup_rollbar import rollbar_handler
from app.models.story import GetStory
from bson import ObjectId

router = APIRouter()

@router.post("/create_story")
@rollbar_handler
async def create_story(isu: int, file: UploadFile = File(...)):
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
    update_result = await stories_collection.insert_one(
        {"isu": isu},
        {"url": file_url},
        {"expiration_date": expiration_date}
    )
    
    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Story cannot be inserted")
    
    return {"expDate": expiration_date, "id": str(update_result.inserted_id)}

@router.get("/get_story/")
@rollbar_handler
async def get_story(payload: GetStory):
    stories_collection = db_instance.get_collection("stories")
    has_access = True  # TODO: Implement access control logic
    
    if not has_access:
        raise HTTPException(status_code=403, detail="Access denied")
    
    story = await stories_collection.find_one({"_id": ObjectId(payload.story_id)})
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    return {
        "id": str(story["_id"]),
        "isu": story["isu"],
        "url": story["url"],
        "expiration_date": story["expiration_date"]
    }


@router.get("/get_user_stories/{isu}")
@rollbar_handler
async def get_user_stories(isu: int):
    stories_collection = db_instance.get_collection("stories")
    cursor = stories_collection.find({"isu": isu})
    stories = await cursor.to_list(length=None)
    if not stories:
        raise HTTPException(status_code=404, detail="User has no stories")
    story_ids = [str(story['_id']) for story in stories]
    return {"stories": story_ids}