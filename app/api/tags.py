from fastapi import APIRouter

from app.utils.db import db_instance
from app.setup_rollbar import rollbar_handler

router = APIRouter()


@router.get("/tags")
@rollbar_handler
async def get_tags():
    tags_collection = db_instance.get_collection("tags")
    tags_cursor = tags_collection.find({"is_special": 0})
    tags = await tags_cursor.to_list(length=None)
    formatted_tags = [{"id": str(tag["_id"]), "text": tag["name"], "icon": "tag"} for tag in tags]
    return formatted_tags

@router.get("/preferences")
@rollbar_handler
async def get_preferences():
    preferences = await db_instance.get_special_tags()
    formatted_preferences = [
        {"id": preference["id"], "text": preference["name"], "icon": "relationship_preferences"} for preference in preferences
    ]
    return {"preferences": formatted_preferences}
