from fastapi import APIRouter, HTTPException
from app.utils.db import db_instance
from app.setup_rollbar import rollbar_handler
from app.models.match import UserAction

router = APIRouter()


@router.get("/random_person")
@rollbar_handler
async def get_random_person(user_id: int):
    person = await db_instance.get_random_person(user_id)
    if not person:
        raise HTTPException(status_code=404, detail="No more persons available")


    def clean_object_key(object_key: str) -> str:
        bucket_prefix = f"{db_instance.minio_bucket_name}/"
        if object_key.startswith(bucket_prefix):
            return object_key[len(bucket_prefix):]
        return object_key

    if person.get("logo"):
        cleaned_logo_key = clean_object_key(person["logo"])
        person["logo"] = db_instance.generate_presigned_url(cleaned_logo_key)
    else:
        person["logo"] = None
    
    response_data = {
        "isu": person["isu"],
        "username": person.get("username", ""),
        "bio": person.get("bio", ""),
        "logo": person.get("logo", ""),
    }

    return response_data


@router.post("/like_person")
@rollbar_handler
async def like_person(payload: UserAction):
    result = await db_instance.like_user(payload.user_id, payload.target_id)

    if result["matched"]:
        return {
            "message": "You have a match!",
            "matched": True,
            "chat_id": result["chat_id"],
        }
    return {"message": "person liked successfully", "matched": False}


@router.post("/dislike_person")
@rollbar_handler
async def dislike_person(payload: UserAction):
    await db_instance.dislike_user(payload.user_id, payload.target_id)
    return {"message": "person disliked successfully"}


@router.get("/liked_me")
@rollbar_handler
async def get_matches(isu: int):
    likes = await db_instance.db["likes"].find({"target_id": isu}).to_list(length=None)

    if not likes:
        return []

    user_ids = [like["user_id"] for like in likes]

    users = await db_instance.db["users"].find({"isu": {"$in": user_ids}}).to_list(length=None)

    result = []
    for user in users:
        user_data = {
            "isu": user["isu"],
            "username": user.get("username", ""),
            "bio": user.get("bio", ""),
            "logo": user.get("logo", ""),
            "photos": user.get("photos", []),
            "mainFeatures": user.get("mainFeatures", []),
            "interests": user.get("interests", []),
            "itmo": user.get("itmo", []),
            "gender_preferences": user.get("gender_preferences", []),
            "relationship_preferences": user.get("relationship_preferences", []),
            "isStudent": user.get("isStudent", True),
        }
        result.append(user_data)

    return result
