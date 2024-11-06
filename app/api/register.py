from fastapi import APIRouter, HTTPException, UploadFile, File

from app.utils.db import db_instance
from app.models.tag import TagSelectionModel
from app.models.user import UsernameSelectionModel, GenderPreferencesSelectionModel, RelationshipsPreferencesSelectionModel
from app.models.profileDetails import ProfileDetailsModel
from uuid import uuid4
from typing import List

router = APIRouter()


@router.post("/register/select_username")
async def select_username(payload: UsernameSelectionModel):
    user_collection = db_instance.get_collection("users")

    update_result = await user_collection.update_one(
        {"isu": payload.isu},
        {"$set": {"username": payload.username}}
    )

    if update_result.modified_count == 0:
        raise HTTPException(
            status_code=404, detail="User not found or username not updated"
        )

    return {"message": "Username updated successfully"}

@router.post("/register/select_preferences")
async def select_preferences(payload: GenderPreferencesSelectionModel):
    user_collection = db_instance.get_collection("users")

    update_result = await user_collection.update_one(
        {"isu": payload.isu},
        {"$set": {"preferences.gender_preference": payload.gender_preference}}
    )

    if update_result.modified_count == 0:
        raise HTTPException(
            status_code=404, detail="User not found or preference not updated"
        )

    return {"message": "Gender preference updated successfully"}

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


@router.post("/register/upload_logo")
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
        {"isu": isu}, {"$set": {"photos.logo": file_url}}
    )

    if update_result.modified_count == 0:
        raise HTTPException(
            status_code=404, detail="User not found or logo not uploaded"
        )
    return {"message": "Avatar uploaded successfully", "avatar_url": file_url}


@router.post("/register/upload_carousel")
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
        {"isu": isu}, {"$set": {"photos.carousel": carousel_urls}}
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


@router.post("/register/select_relationship")
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

    selected_tag_ids = [str(tag["_id"]) for tag in special_tags if tag["name"] in user_selected_tags]

    update_result = await user_collection.update_one(
        {"isu": payload.isu},
        {"$set": {"preferences.relationship_preference": selected_tag_ids}}
    )

    if update_result.modified_count == 0:
        raise HTTPException(
            status_code=404, detail="User not found or relationship preference not updated"
        )

    return {"message": "Relationship preference updated successfully"}
