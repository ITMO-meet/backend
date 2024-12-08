from fastapi import APIRouter, HTTPException
from uuid import uuid4
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

    return{
        "id": person["isu"],
        "name": person.get("name",""),
        "description": person.get("description",""),
        "imageUrl": person.get("imageUrl", "")
    }

@router.post("/like_person")
@rollbar_handler
async def like_person(payload: UserAction):
    result = await db_instance.like_user(payload.user_id, payload.target_id)
    return result

@router.post("/dislike_person")
@rollbar_handler
async def dislike_person(payload: UserAction):
    await db_instance.dislike_user(payload.user_id, payload.target_id)
    return {"status": "ok"}

@router.get("liked_me")
@rollbar_handler
async def get_matches(isu: int):
    likes = await db_instance.db["likes"].find({"target_id": isu}).to_list(length=None)

    if not likes: return []

    user_ids = [like["user_id"] for like in likes]

    users = await db_instance.db["users"].find({"isu": {"$in": user_ids}})

    result = []
    for user in users:
        isu = user.get("isu", 0)
        username = user.get("username", "")
        bio = user.get("bio", "")
        photos_info = user.get("photos", {})
        logo = photos_info.get("logo", "")
        carousel = photos_info.get("carousel", [])
        
        person_params = user.get("person_params", {})
        height = person_params.get("height", None)
        faculty = person_params.get("faculty", None)
        zodiac = person_params.get("zodiac_sign", None)

        mainFeatures = []
        if height:
            mainFeatures.append({"text": f"{height} cm", "icon": "StraightenIcon"})
        if zodiac:
            mainFeatures.append({"text": zodiac, "icon": "ZodiacIcon"})

        interests = []  
        itmo = []
        if faculty:
            itmo.append({"text": faculty, "icon": "HomeIcon"})
        itmo.append({"text": str(isu), "icon": "BadgeIcon"})
        
        user_data = {
            "id": isu,  
            "name": username, 
            "description": bio,  
            "imageUrl": logo, 
            "photos": carousel,  
            "mainFeatures": mainFeatures,
            "interests": interests,
            "itmo": itmo,
            "isStudent": True  
        }
        result.append(user_data)

    return result
        