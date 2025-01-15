from fastapi import APIRouter, Form, HTTPException, File, UploadFile, Depends
from uuid import uuid4
from datetime import datetime, timedelta
from app.utils.db import db_instance
from app.setup_rollbar import rollbar_handler
from app.models.story import GetStory
from bson import ObjectId

router = APIRouter()


@router.post("/create_story")
@rollbar_handler
async def create_story(
    isu: int = Form(...),
    file: UploadFile = File(...)
):
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

    story_document = {"isu": isu, "url": file_url, "expiration_date": expiration_date}

    insert_result = await stories_collection.insert_one(story_document)

    if not insert_result.inserted_id:
        raise HTTPException(status_code=404, detail="Story cannot be inserted")

    return {"expDate": expiration_date, "id": str(insert_result.inserted_id)}


@router.get("/get_story/{story_id}")
@rollbar_handler
async def get_story(story_id: str):
    stories_collection = db_instance.get_collection("stories")
    has_access = True  # TODO: Implement access control logic

    if not has_access:
        raise HTTPException(status_code=403, detail="Access denied")

    story = await stories_collection.find_one({"_id": ObjectId(story_id)})

    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    path = story["url"]
    bucket_prefix = f"{db_instance.minio_bucket_name}/"
    if path.startswith(bucket_prefix):
        path = path[len(bucket_prefix) :]

    presigned_url = db_instance.generate_presigned_url(object_name=path, expiration=timedelta(hours=3))

    return {
        "id": str(story["_id"]),
        "isu": story["isu"],
        "url": presigned_url,
        "expiration_date": story["expiration_date"],
    }


@router.get("/get_user_stories/{isu}")
@rollbar_handler
async def get_user_stories(isu: int):
    stories_collection = db_instance.get_collection("stories")
    cursor = stories_collection.find({"isu": isu})
    stories = await cursor.to_list(length=None)
    if not stories:
        return {"stories": []}
    story_ids = [str(story["_id"]) for story in stories]
    return {"stories": story_ids}
