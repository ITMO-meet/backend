from fastapi import APIRouter, HTTPException
from app.utils.db import db_instance
from bson import ObjectId
from datetime import timedelta

router = APIRouter()

@router.get("/get_profile/{isu}")
async def get_profile(isu: int):
    user_collection = db_instance.get_collection("users")
    tags_collection = db_instance.get_collection("tags")

    user = await user_collection.find_one({"isu": isu})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    tag_ids = [ObjectId(tag_id) for tag_id in user.get("tags", [])]
    preference_ids = [ObjectId(pref_id) for pref_id in user["preferences"].get("relationship_preference", [])]

    user_tags = await tags_collection.find({"_id": {"$in": tag_ids}}).to_list(length=None)
    user_preferences = await tags_collection.find({"_id": {"$in": preference_ids}}).to_list(length=None)
    
    tags = [tag["name"] for tag in user_tags]
    preferences = [pref["name"] for pref in user_preferences]

    logo_url = None
    if "logo" in user["photos"]:
        logo_url = db_instance.minio_instance.presigned_get_object(
            db_instance.minio_bucket_name, user["photos"]["logo"], expires=timedelta(seconds=3600)
        )
    
    carousel_urls = [
        db_instance.minio_instance.presigned_get_object(
            db_instance.minio_bucket_name, photo, expires=timedelta(seconds=3600)
        ) for photo in user["photos"].get("carousel", [])
    ]

    profile_data = {
        "username": user["username"],
        "bio": user.get("bio", ""),
        "tags": tags,
        "preferences": preferences,
        "photos": {
            "logo": logo_url,
            "carousel": carousel_urls
        },
        "person_params": {
            "zodiac_sign": user["person_params"].get("zodiac_sign"),
            "height": user["person_params"].get("height"),
            "weight": user["person_params"].get("weight")
        }
    }
    
    return {"profile": profile_data}

@router.put("/update_bio/{isu}")
async def update_bio(isu: int, bio: str):
    user_collection = db_instance.get_collection("users")
    update_result = await user_collection.update_one(
        {"isu": isu},
        {"$set": {"bio": bio}}
    )

    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found or bio not updated")
    
    return {"message": "bio updated successfully"}

@router.put("/update_username/{isu}")
async def update_username(isu: int, username: str):
    user_collection = db_instance.get_collection("users")
    update_result = await user_collection.update_one(
        {"isu": isu},
        {"$set": {"username": username}}
    )

    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found or username not updated")
    
    return {"messahe": "username updated successfully"}

@router.put("/update_height/{isu}")
async def update_height(isu: int, height: float):
    user_collection = db_instance.get_collection("users")
    update_result = await user_collection.update_one(
        {"isu": isu},
        {"$set": {"person_params.height": height}}
    )

    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found or height not updated")
    
    return {"messahe": "height updated successfully"}

@router.put("/update_height/{isu}")
async def update_weight(isu: int, weight: float):
    user_collection = db_instance.get_collection("users")
    update_result = await user_collection.update_one(
        {"isu": isu},
        {"$set": {"person_params.weight": weight}}
    )

    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found or weight not updated")
    
    return {"messahe": "weight updated successfully"}