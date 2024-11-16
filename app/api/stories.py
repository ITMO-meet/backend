# app/api/stories.py

from fastapi import APIRouter
from app.setup_rollbar import rollbar_handler

router = APIRouter()

@router.get("/stories")
@rollbar_handler
async def get_stories():
    stories = [
        {
            "id": 1,
            "name": "Alice",
            "pfp": "https://randomuser.me/api/portraits/women/1.jpg",
            "stories": [
                {
                    "id": 1,
                    "image": "https://source.unsplash.com/random/800x600",
                    "expiresAt": 1234567890,
                }
            ],
        },
    ]
    return {"stories": stories}
