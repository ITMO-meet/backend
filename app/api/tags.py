from fastapi import APIRouter

from app.utils.db import db_instance
from app.setup_rollbar import rollbar_handler

router = APIRouter()


@router.get("/tags")
@rollbar_handler
async def get_tags():
    tags = await db_instance.get_available_tags()
    formatted_tags = [{"text": tag["name"], "icon": "tag"} for tag in tags]
    return {"tags": formatted_tags}

@router.get("/preferences")
@rollbar_handler
async def get_preferences():
    preferences = await db_instance.get_special_tags()
    formatted_preferences = [
        {"text": preference["name"], "icon": "relationship_preferences"}
        for preference in preferences
    ]
    return {"preferences": formatted_preferences}
