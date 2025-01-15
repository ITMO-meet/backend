from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, HTTPException

from app.models.match import UserAction
from app.setup_rollbar import rollbar_handler
from app.utils.db import db_instance

router = APIRouter()


@router.get("/random_person")
@rollbar_handler
async def get_random_person(user_id: int):
    person = await db_instance.get_random_person(user_id)
    if not person:
        raise HTTPException(status_code=404, detail="No more persons available")

    person["_id"] = str(person["_id"])

    def clean_object_key(object_key: str) -> str:
        bucket_prefix = f"{db_instance.minio_bucket_name}/"
        if object_key.startswith(bucket_prefix):
            return object_key[len(bucket_prefix) :]
        return object_key

    if person.get("logo"):
        cleaned_logo_key = clean_object_key(person["logo"])
        person["logo"] = db_instance.generate_presigned_url(cleaned_logo_key)
    else:
        person["logo"] = None

    if person.get("photos"):
        person["photos"] = [db_instance.generate_presigned_url(clean_object_key(photo)) for photo in person["photos"]]
    else:
        person["photos"] = []

    response_data = {
        "profile": {
            "isu": person["isu"],
            "username": person.get("username", ""),
            "bio": person.get("bio", ""),
            "logo": person.get("logo", ""),
            "photos": person.get("photos", []),
            "mainFeatures": person.get("mainFeatures", []),
            "interests": person.get("interests", []),
            "itmo": person.get("itmo", []),
            "gender_preferences": person.get("gender_preferences", []),
            "relationship_preferences": person.get("relationship_preferences", []),
            "isStudent": person.get("isStudent", True),
        }
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


@router.post("/superlike_person")
@rollbar_handler
async def superlike_person(payload: UserAction):
    result = await db_instance.like_user(payload.user_id, payload.target_id)

    reverse_like = await db_instance.db["likes"].find_one({"user_id": payload.target_id, "target_id": payload.user_id})

    if not reverse_like:
        await db_instance.db["likes"].insert_one(
            {
                "user_id": payload.target_id,
                "target_id": payload.user_id,
                "created_at": datetime.now(timezone.utc),
            }
        )

    if result.get("matched"):
        return {
            "message": "You have a match!",
            "matched": True,
            "chat_id": result["chat_id"],
        }
    else:
        chat_id = str(ObjectId())
        await db_instance.create_chat(chat_id=chat_id, isu_1=payload.user_id, isu_2=payload.target_id)

        return {
            "message": "You have a match!",
            "matched": True,
            "chat_id": chat_id,
        }


@router.post("/dislike_person")
@rollbar_handler
async def dislike_person(payload: UserAction):
    await db_instance.dislike_user(payload.user_id, payload.target_id)
    return {"message": "person disliked successfully"}


@router.post("/block_person")
@rollbar_handler
async def block_person(payload: UserAction):
    result = await db_instance.db["chats"].delete_one(
        {
            "$or": [
                {"isu_1": payload.user_id, "isu_2": payload.target_id},
                {"isu_1": payload.target_id, "isu_2": payload.user_id},
            ]
        }
    )

    if result.deleted_count > 0:
        return {"message": "user blocked, chat deleted"}
    else:
        raise HTTPException(status_code=404, details="chat not found or user already blocked")


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
