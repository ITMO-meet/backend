import html
import os
import re
import urllib.parse
from base64 import urlsafe_b64encode
from hashlib import sha256

from aiohttp import ClientSession
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse

from app.models.user import UserModel
from app.utils.db import db_instance

router = APIRouter()

router.get("/tags")
async def get_tags():
    tags = await db_instance.get_available_tags()
    return {"tags": tags}