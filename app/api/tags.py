from fastapi import APIRouter

from app.utils.db import db_instance

router = APIRouter()

@router.get("/tags")
async def get_tags():
    tags = await db_instance.get_available_tags()
    return {"tags": tags}