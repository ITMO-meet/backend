from fastapi import APIRouter, HTTPException

from app.utils.db import db_instance
from app.models.tag import TagSelectionModel
from app.models.profileDetails import ProfileDetailsModel

router = APIRouter()


@router.post("/register/select_tags")
async def select_tags(payload: TagSelectionModel):
    user_collection = db_instance.get_collection("users")
    tags_collection = db_instance.get_collection("tags")

    tag_objects = await tags_collection.find({"name": {"$in": payload.tags}}).to_list(
        length=None
    )
    tag_ids = [str(tag["_id"]) for tag in tag_objects]

    if not tag_ids:
        raise HTTPException(status_code=404, detail="Tags not found")

    update_result = await user_collection.update_one(
        {"isu": payload.isu}, {"$set": {"tags": tag_ids}}
    )

    if update_result.modified_count == 0:
        raise HTTPException(
            status_code=404, detail="User not found or tags not updated"
        )

    return {"message": "Tags selected successfully, proceed to the next step"}


@router.post("/register/profile_details")
async def add_profile_details(payload: ProfileDetailsModel):
    user_collection = db_instance.get_collection("users")

    data = {
        "bio": payload.bio,
        "person_params.weight": payload.weight,
        "person_params.height": payload.height,
        "person_params.hair_color": payload.hair_color,
        "person_params.zodiac_sign": payload.zodiac_sign,
    }

    data = {k: v for k, v in data.items() if v is not None}

    update_result = await user_collection.update_one(
        {"isu": payload.isu}, {"$set": data}
    )

    if update_result.modified_count == 0:
        raise HTTPException(
            status_code=404, detail="User not found or profile not updated"
        )

    return {"message": "Profile details updated successfully"}
