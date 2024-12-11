from fastapi import APIRouter, HTTPException, File, UploadFile
from app.utils.db import db_instance
from app.models.tag import TagSelectionModel
from app.models.user import GenderPreferencesSelectionModel, UsernameSelectionModel
from app.setup_rollbar import rollbar_handler
from bson import ObjectId
from datetime import timedelta
from uuid import uuid4

router = APIRouter()


@router.get("/get_profile/{isu}")
@rollbar_handler
async def get_profile(isu: int):
    user_collection = db_instance.get_collection("users")
    user = await user_collection.find_one({"isu": isu})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"profile": user}


@router.put("/update_bio/{isu}")
@rollbar_handler
async def update_bio(isu: int, bio: str):
    user_collection = db_instance.get_collection("users")
    update_result = await user_collection.update_one(
        {"isu": isu}, {"$set": {"bio": bio}}
    )

    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found or bio not updated")

    return {"message": "bio updated successfully"}


@router.put("/update_username")
@rollbar_handler
async def update_username(payload: UsernameSelectionModel):
    user_collection = db_instance.get_collection("users")
    update_result = await user_collection.update_one(
        {"isu": payload.isu}, {"$set": {"username": payload.username}}
    )

    if update_result.modified_count == 0:
        raise HTTPException(
            status_code=404, detail="User not found or username not updated"
        )

    return {"message": "username updated successfully"}


@router.put("/update_height/{isu}")
@rollbar_handler
async def update_height(isu: int, height: float):
    user_collection = db_instance.get_collection("users")
    update_result = await user_collection.update_one(
        {"isu": isu}, {"$set": {"mainFeatures.0.text": f"{height} cm"}}
    )

    if update_result.modified_count == 0:
        raise HTTPException(
            status_code=404, detail="User not found or height not updated"
        )

    return {"message": "height updated successfully"}


@router.put("/update_weight/{isu}")
@rollbar_handler
async def update_weight(isu: int, weight: float):
    user_collection = db_instance.get_collection("users")
    update_result = await user_collection.update_one(
        {"isu": isu}, {"$set": {"mainFeatures.2.text": f"{weight} kg"}}
    )

    if update_result.modified_count == 0:
        raise HTTPException(
            status_code=404, detail="User not found or weight not updated"
        )

    return {"message": "weight updated successfully"}


@router.put("/update_zodiac/{isu}")
@rollbar_handler
async def update_zodiac_sign(isu: int, zodiac_sign: str):
    user_collection = db_instance.get_collection("users")
    update_result = await user_collection.update_one(
        {"isu": isu}, {"$set": {"mainFeatures.1.text": zodiac_sign}}
    )

    if update_result.modified_count == 0:
        raise HTTPException(
            status_code=404, detail="User not found or zodiac sign not updated"
        )

    return {"message": "Zodiac sign updated successfully"}


@router.put("/update_tags")
@rollbar_handler
async def update_tags(payload: TagSelectionModel):
    user_collection = db_instance.get_collection("users")
    tags_collection = db_instance.get_collection("tags")

    tag_ids = [ObjectId(tag_id) for tag_id in payload.tags]
    existing_tags = await tags_collection.find({"_id": {"$in": tag_ids}}).to_list(
        length=None
    )

    if len(existing_tags) != len(tag_ids):
        raise HTTPException(status_code=400, detail="Some tags do not exist")

    interests = [
        {"text": tag["name"], "icon": "tag"}
        for tag in existing_tags
        if tag["is_special"] == 0
    ]

    update_result = await user_collection.update_one(
        {"isu": payload.isu}, {"$set": {"interests": interests}}
    )

    if update_result.modified_count == 0:
        raise HTTPException(
            status_code=404, detail="User not found or tags not updated"
        )

    return {"message": "tags updated successfully"}


@router.put("/update_relationship_preferences")
@rollbar_handler
async def update_relationship_preferences(payload: TagSelectionModel):
    user_collection = db_instance.get_collection("users")
    tags_collection = db_instance.get_collection("tags")

    tag_ids = [ObjectId(tag_id) for tag_id in payload.tags]
    special_tags = await tags_collection.find(
        {"_id": {"$in": tag_ids}, "is_special": 1}
    ).to_list(length=None)

    if len(special_tags) != len(tag_ids):
        raise HTTPException(
            status_code=400, detail="Some tags do not exist or are not special tags"
        )

    relationship_preferences = [
        {"text": str(tag["_id"]), "icon": "relationship_preferences"}
        for tag in special_tags
    ]

    update_result = await user_collection.update_one(
        {"isu": payload.isu},
        {"$set": {"relationship_preferences": relationship_preferences}},
    )

    if update_result.modified_count == 0:
        raise HTTPException(
            status_code=404, detail="User not found or preferences not updated"
        )

    return {"message": "relationship preferences updated successfully"}


@router.put("/update_logo/{isu}")
@rollbar_handler
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
        {"isu": isu}, {"$set": {"logo": file_url}}
    )

    if update_result.modified_count == 0:
        raise HTTPException(
            status_code=404, detail="User not found or logo not updated"
        )

    return {"message": "logo updated successfully", "logo_url": file_url}


@router.put("/update_carousel_photo/{isu}")
@rollbar_handler
async def update_carousel_photo(
    isu: int, old_photo_url: str, new_file: UploadFile = File(...)
):
    user_collection = db_instance.get_collection("users")

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

    photos = user.get("photos", [])
    if old_photo_url not in photos:
        raise HTTPException(status_code=404, detail="Photo not found in carousel")

    updated_photos = [
        new_file_url if photo == old_photo_url else photo for photo in photos
    ]

    update_result = await user_collection.update_one(
        {"isu": isu}, {"$set": {"photos": updated_photos}}
    )

    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Photo not updated in carousel")

    return {
        "message": "carousel photo updated successfully",
        "new_photo_url": new_file_url,
    }


@router.delete("/delete_carousel_photo/{isu}")
@rollbar_handler
async def delete_carousel_photo(isu: int, photo_url: str):
    user_collection = db_instance.get_collection("users")

    try:
        db_instance.minio_instance.remove_object(
            db_instance.minio_bucket_name, photo_url
        )
    except Exception:
        raise HTTPException(
            status_code=500, detail="Failed to delete photo from storage"
        )

    user = await user_collection.find_one({"isu": isu})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    photos = user.get("photos", [])
    if photo_url not in photos:
        raise HTTPException(status_code=404, detail="Photo not found in carousel")

    updated_photos = [photo for photo in photos if photo != photo_url]

    update_result = await user_collection.update_one(
        {"isu": isu}, {"$set": {"photos": updated_photos}}
    )

    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Photo not removed from carousel")

    return {"message": "carousel photo deleted successfully"}


@router.put("/update_gender_preference")
@rollbar_handler
async def update_gender_preference(payload: GenderPreferencesSelectionModel):
    user_collection = db_instance.get_collection("users")

    update_result = await user_collection.update_one(
        {"isu": payload.isu},
        {
            "$set": {
                "gender_preferences": [
                    {"text": payload.gender_preference, "icon": "gender_preferences"}
                ]
            }
        },
    )

    if update_result.modified_count == 0:
        raise HTTPException(
            status_code=404, detail="User not found or gender preference not updated"
        )

    return {"message": "gender preference updated successfully"}
