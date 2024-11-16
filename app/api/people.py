# app/api/people.py

from fastapi import APIRouter, HTTPException, Query
from app.setup_rollbar import rollbar_handler
from app.utils.db import db_instance
from typing import Optional


router = APIRouter()

@router.get("/people")
@rollbar_handler
async def get_people(current_user_id: Optional[int] = Query(None)):
    people = [
        {
            "id": 2,  # Use numeric IDs
            "name": "Bob",
            "description": "Loves hiking and outdoor activities.",
            "imageUrl": "https://randomuser.me/api/portraits/men/2.jpg",
        },
    ]
    return {"people": people}

    # Fetch people excluding those already interacted with by the current user
    # people = await db_instance.get_people(current_user_id)
    # return {"people": people}

@router.post("/people/{person_id}/like")
@rollbar_handler
async def like_person(person_id: int, current_user_id: int = Query(...)):
    await db_instance.like_person(current_user_id, person_id)
    return {"message": "Person liked"}

@router.post("/people/{person_id}/dislike")
@rollbar_handler
async def dislike_person(person_id: int, current_user_id: int = Query(...)):
    await db_instance.dislike_person(current_user_id, person_id)
    return {"message": "Person disliked"}

@router.post("/people/{person_id}/superlike")
@rollbar_handler
async def superlike_person(person_id: int, current_user_id: int = Query(...)):
    await db_instance.superlike_person(current_user_id, person_id)
    return {"message": "Person superliked"}