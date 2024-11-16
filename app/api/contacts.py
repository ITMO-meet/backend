# app/api/contacts.py

from fastapi import APIRouter
from app.setup_rollbar import rollbar_handler

router = APIRouter()

# app/api/contacts.py

@router.get("/contacts")
@rollbar_handler
async def get_contacts():
    contacts = [
        {
            "id": 1,
            "name": "Alice",
            "pfp": "https://randomuser.me/api/portraits/women/1.jpg",
            "lastMessage": "Hey, how are you?",
            "stories": [
                {
                    "id": 1,
                    "image": "https://source.unsplash.com/random/800x600",
                    "expiresAt": 1234567890,
                }
            ],
        },
    ]
    return {"contacts": contacts}
