from fastapi import APIRouter, HTTPException, File, UploadFile
from app.utils.db import db_instance
from app.models.tag import TagSelectionModel
from bson import ObjectId
from datetime import timedelta
from uuid import uuid4

router = APIRouter()


@router.get("/get_profile/{isu}")
async def get_profile(isu: int):
    user_collection = db_instance.get_collection("users")
    tags_collection = db_instance.get_collection("tags")

    user = await user_collection.find_one({"isu": isu})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    tag_ids = [ObjectId(tag_id) for tag_id in user.get("tags", [])]
    preference_ids = [
        ObjectId(pref_id)
        for pref_id in user["preferences"].get("relationship_preference", [])
    ]

    user_tags = await tags_collection.find({"_id": {"$in": tag_ids}}).to_list(
        length=None
    )
    user_preferences = await tags_collection.find(
        {"_id": {"$in": preference_ids}}
    ).to_list(length=None)

    tags = [tag["name"] for tag in user_tags]
    preferences = [pref["name"] for pref in user_preferences]

    logo_url = None
    if "logo" in user["photos"]:
        logo_url = db_instance.minio_instance.presigned_get_object(
            db_instance.minio_bucket_name,
            user["photos"]["logo"],
            expires=timedelta(seconds=3600),
        )

    carousel_urls = [
        db_instance.minio_instance.presigned_get_object(
            db_instance.minio_bucket_name, photo, expires=timedelta(seconds=3600)
        )
        for photo in user["photos"].get("carousel", [])
    ]

    profile_data = {
        "username": user["username"],
        "bio": user.get("bio", ""),
        "tags": tags,
        "preferences": preferences,
        "photos": {"logo": logo_url, "carousel": carousel_urls},
        "person_params": {
            "zodiac_sign": user["person_params"].get("zodiac_sign"),
            "height": user["person_params"].get("height"),
            "weight": user["person_params"].get("weight"),
        },
    }

    return {"profile": profile_data}


@router.put("/update_bio/{isu}")
async def update_bio(isu: int, bio: str):
    user_collection = db_instance.get_collection("users")
    update_result = await user_collection.update_one(
        {"isu": isu}, {"$set": {"bio": bio}}
    )

    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found or bio not updated")

    return {"message": "bio updated successfully"}


@router.put("/update_username/{isu}")
async def update_username(isu: int, username: str):
    user_collection = db_instance.get_collection("users")
    update_result = await user_collection.update_one(
        {"isu": isu}, {"$set": {"username": username}}
    )

    if update_result.modified_count == 0:
        raise HTTPException(
            status_code=404, detail="User not found or username not updated"
        )

    return {"messahe": "username updated successfully"}


@router.put("/update_height/{isu}")
async def update_height(isu: int, height: float):
    user_collection = db_instance.get_collection("users")
    update_result = await user_collection.update_one(
        {"isu": isu}, {"$set": {"person_params.height": height}}
    )

    if update_result.modified_count == 0:
        raise HTTPException(
            status_code=404, detail="User not found or height not updated"
        )

    return {"messahe": "height updated successfully"}


@router.put("/update_height/{isu}")
async def update_weight(isu: int, weight: float):
    user_collection = db_instance.get_collection("users")
    update_result = await user_collection.update_one(
        {"isu": isu}, {"$set": {"person_params.weight": weight}}
    )

    if update_result.modified_count == 0:
        raise HTTPException(
            status_code=404, detail="User not found or weight not updated"
        )

    return {"messahe": "weight updated successfully"}


@router.put("/update_zodiac/{isu}")
async def update_zodiac_sign(isu: int, zodiac_sign: str):
    user_collection = db_instance.get_collection("users")
    update_result = await user_collection.update_one(
        {"isu": isu}, {"$set": {"person_params.zodiac_sign": zodiac_sign}}
    )

    if update_result.modified_count == 0:
        raise HTTPException(
            status_code=404, detail="User not found or zodiac sign not updated"
        )

    return {"message": "Zodiac sign updated successfully"}

@router.put("/update_tags")
async def update_tags(payload: TagSelectionModel):
    user_collection = db_instance.get_collection("users")
    tags_collection = db_instance.get_collection("tags")

    tag_ids = [ObjectId(tag_id) for tag_id in payload.tags]
    existing_tags = await tags_collection.find({"_id": {"$in": tag_ids}}).to_list(length=None)

    if len(existing_tags) != len(tag_ids):
        raise HTTPException(status_code=400, detail="Some tags do not exist")

    update_result = await user_collection.update_one(
        {"isu": payload.isu},
        {"$set": {"tags": tag_ids}}
    )

    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found or tags not updated")

    return {"message": "tags updated successfully"}

@router.put("/update_relationship_preferences")
async def update_relationship_preferences(payload: TagSelectionModel):
    user_collection = db_instance.get_collection("users")
    tags_collection = db_instance.get_collection("tags")

    tag_ids = [ObjectId(tag_id) for tag_id in payload.tags]
    special_tags = await tags_collection.find({"_id": {"$in": tag_ids}, "is_special": 1}).to_list(length=None)

    if len(special_tags) != len(tag_ids):
        raise HTTPException(status_code=400, detail="Some tags do not exist or are not special tags")

    update_result = await user_collection.update_one(
        {"isu": payload.isu},
        {"$set": {"preferences.relationship_preference": tag_ids}}
    )

    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found or preferences not updated")

    return {"message": "relationship preferences updated successfully"}


@router.put("/update_logo/{isu}")
async def update_logo(isu: int, file: UploadFile = File(...)):
    user_collection = db_instance.get_collection("users")

    file_extension = file.filename.split(".")[-1]
    filename = f"logos/{isu}_{uuid4()}.{file_extension}"
    file_url = db_instance.upload_file_to_minio(
        file.file,
        filename,
        content_type=file.content_type or "application/octet-stream",
    )

    update_result = await user_collection.update_one(
        {"isu": isu}, {"$set": {"photos.logo": file_url}}
    )

    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found or logo not updated")

    return {"message": "logo updated successfully", "logo_url": file_url}

@router.put("/update_carousel_photo/{isu}")
async def update_carousel_photo(isu: int, old_photo_url: str, new_file: UploadFile = File(...)):
    user_collection = db_instance.get_collection("users")

    db_instance.minio_instance.remove_object(db_instance.minio_bucket_name, old_photo_url)

    file_extension = new_file.filename.split(".")[-1]
    new_filename = f"carousel/{isu}_{uuid4()}.{file_extension}"
    new_file_url = db_instance.upload_file_to_minio(
        new_file.file,
        new_filename,
        content_type=new_file.content_type or "application/octet-stream",
    )
    user = await user_collection.find_one({"isu": isu})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    carousel = user["photos"].get("carousel", [])
    if old_photo_url not in carousel:
        raise HTTPException(status_code=404, detail="Photo not found in carousel")

    carousel = [new_file_url if photo == old_photo_url else photo for photo in carousel]
    update_result = await user_collection.update_one(
        {"isu": isu}, {"$set": {"photos.carousel": carousel}}
    )

    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Photo not updated in carousel")

    return {"message": "carousel photo updated successfully", "new_photo_url": new_file_url}
