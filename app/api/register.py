import html
import os
import re
import urllib.parse
from base64 import urlsafe_b64encode
from hashlib import sha256
from typing import List
from aiohttp import ClientSession
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse

from app.models.user import UserModel
from app.utils.db import db_instance

router = APIRouter()


from pydantic import BaseModel

from pydantic import BaseModel
from typing import List

class TagSelectionModel(BaseModel):
    isu: int
    tags: List[str]

@router.post("/register/select_tags")
async def select_tags(payload: TagSelectionModel):
    user_collection = db_instance.get_collection("users")
    tags_collection = db_instance.get_collection("tags")

    tag_names = payload.tags
    isu = payload.isu

    tag_objects = await tags_collection.find({"name": {"$in": tag_names}}).to_list(length=None)
    tag_ids = [str(tag["_id"]) for tag in tag_objects]

    if not tag_ids:
        raise HTTPException(status_code=404, detail="Tags not found")

    update_result = await user_collection.update_one(
        {"isu": isu},
        {"$set": {"tags": tag_ids}}
    )

    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found or tags not updated")

    return {"message": "Tags selected successfully, proceed to the next step"}

