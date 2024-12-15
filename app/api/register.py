from fastapi import APIRouter, HTTPException, UploadFile, File

from app.utils.db import db_instance
from app.models.tag import TagSelectionModel
from app.models.user import (
    UsernameSelectionModel,
    GenderPreferencesSelectionModel,
    RelationshipsPreferencesSelectionModel,
)
from app.models.profileDetails import ProfileDetailsModel
from app.setup_rollbar import rollbar_handler
from uuid import uuid4
from typing import List
from bson import ObjectId

router = APIRouter()


@router.post("/register/select_username")
@rollbar_handler
async def select_username(payload: UsernameSelectionModel):
    user_collection = db_instance.get_collection("users")

    update_result = await user_collection.update_one(
        {"isu": payload.isu}, {"$set": {"username": payload.username}}
    )

    if update_result.modified_count == 0:
        raise HTTPException(
            status_code=404, detail="User not found or username not updated"
        )

    return {"message": "Username updated successfully"}


@router.post("/register/select_preferences")
@rollbar_handler
async def select_preferences(payload: GenderPreferencesSelectionModel):
    user_collection = db_instance.get_collection("users")

    update_result = await user_collection.update_one(
        {"isu": payload.isu},
        {
            "$set": {
                "gender_preferences": [
                    {"text": payload.gender_preference, "icon": "gender_preferences"}
                ]
            }
        },
    )

    if update_result.modified_count == 0:
        raise HTTPException(
            status_code=404, detail="User not found or preference not updated"
        )

    return {"message": "Gender preference updated successfully"}


@router.post("/register/select_tags")
@rollbar_handler
async def select_tags(payload: TagSelectionModel):
    user_collection = db_instance.get_collection("users")
    tags_collection = db_instance.get_collection("tags")

    tag_ids = [ObjectId(tag_id) for tag_id in payload.tags]
    existing_tags = await tags_collection.find({"_id": {"$in": tag_ids}}).to_list(
        length=None
    )

    if len(existing_tags) != len(tag_ids):
        raise HTTPException(status_code=404, detail="Some tags do not exist")

    interests = [
        {"text": tag["name"], "icon": "tag"}
        for tag in existing_tags
        if tag["is_special"] == 0
    ]

    update_result = await user_collection.update_one(
        {"isu": payload.isu}, {"$set": {"interests": interests}}
    )

    if update_result.modified_count == 0:
        raise HTTPException(
            status_code=404, detail="User not found or tags not updated"
        )

    return {"message": "Tags selected successfully, proceed to the next step"}


@router.post("/register/upload_logo")
@rollbar_handler
async def upload_logo(isu: int, file: UploadFile = File(...)):
    user_collection = db_instance.get_collection("users")

    file_extension = file.filename.split(".")[-1]
    filename = f"logos/{isu}_{uuid4()}.{file_extension}"

    file_url = db_instance.upload_file_to_minio(
        file.file,
        filename,
        content_type=file.content_type or "application/octet-stream",
    )

    update_result = await user_collection.update_one(
        {"isu": isu}, {"$set": {"logo": file_url}}
    )

    if update_result.modified_count == 0:
        raise HTTPException(
            status_code=404, detail="User not found or logo not uploaded"
        )
    return {"message": "Avatar uploaded successfully", "avatar_url": file_url}


@router.post("/register/upload_carousel")
@rollbar_handler
async def upload_carousel(isu: int, files: List[UploadFile] = File(...)):
    user_collection = db_instance.get_collection("users")

    carousel_urls = []

    for file in files:
        file_extension = file.filename.split(".")[-1]
        filename = f"carousel/{isu}_{uuid4()}.{file_extension}"

        file_url = db_instance.upload_file_to_minio(
            file.file,
            filename,
            content_type=file.content_type or "application/octet-stream",
        )

        carousel_urls.append(file_url)

    update_result = await user_collection.update_one(
        {"isu": isu}, {"$set": {"photos": carousel_urls}}
    )

    if update_result.modified_count == 0:
        raise HTTPException(
            status_code=404, detail="User not found or carousel photos not updated"
        )

    return {
        "message": "Carousel photos uploaded successfully",
        "carousel_urls": carousel_urls,
    }


@router.post("/register/profile_details")
@rollbar_handler
async def add_profile_details(payload: ProfileDetailsModel):
    user_collection = db_instance.get_collection("users")

    data = {
        "bio": payload.bio,
        "mainFeatures.0.text": f"{payload.height} cm" if payload.height else "",
        "mainFeatures.2.text": f"{payload.weight} kg" if payload.weight else "",
        "mainFeatures.1.text": payload.zodiac_sign if payload.zodiac_sign else "",
    }

    data = {k: v for k, v in data.items() if v}

    update_result = await user_collection.update_one(
        {"isu": payload.isu}, {"$set": data}
    )

    if update_result.modified_count == 0:
        raise HTTPException(
            status_code=404, detail="User not found or profile details not updated"
        )

    return {"message": "Profile details updated successfully"}


@router.post("/register/select_relationship")
@rollbar_handler
async def select_relationship(payload: RelationshipsPreferencesSelectionModel):
    user_collection = db_instance.get_collection("users")
    tags_collection = db_instance.get_collection("tags")

    special_tags = await tags_collection.find({"is_special": 1}).to_list(length=None)
    special_tag_names = {tag["name"] for tag in special_tags}

    user_selected_tags = set(payload.relationship_preference)
    if not user_selected_tags.issubset(special_tag_names):
        raise HTTPException(
            status_code=400,
            detail="Invalid relationship preference tags provided",
        )

    selected_tag_ids = [
        {"text": tag["name"], "icon": "relationship_preferences"}
        for tag in special_tags
        if tag["name"] in user_selected_tags
    ]

    update_result = await user_collection.update_one(
        {"isu": payload.isu},
        {"$set": {"relationship_preferences": selected_tag_ids}},
    )

    if update_result.modified_count == 0:
        raise HTTPException(
            status_code=404,
            detail="User not found or relationship preferences not updated",
        )

    return {"message": "Relationship preference updated successfully"}
