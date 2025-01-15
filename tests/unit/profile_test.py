import uuid
from io import BytesIO
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from bson import ObjectId
from fastapi import FastAPI
from httpx import AsyncClient

from app.api.profile import router
from app.utils.db import db_instance


@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.mark.asyncio
async def test_update_bio_success(app):
    isu = 123456
    bio = "new bio"
    update_result_mock = AsyncMock()
    update_result_mock.modified_count = 1

    with patch.object(db_instance, "get_collection") as mock_get_collection:
        mock_user_collection = AsyncMock()
        mock_user_collection.update_one.return_value = update_result_mock
        mock_get_collection.return_value = mock_user_collection

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(f"/update_bio/{isu}", params={"bio": bio})

        assert response.status_code == 200
        assert response.json() == {"message": "bio updated successfully"}
        mock_user_collection.update_one.assert_called_once_with({"isu": isu}, {"$set": {"bio": bio}})


@pytest.mark.asyncio
async def test_update_bio_user_not_found(app):
    isu = 123456
    bio = "new bio"
    update_result_mock = AsyncMock()
    update_result_mock.modified_count = 0

    with patch.object(db_instance, "get_collection") as mock_get_collection:
        mock_user_collection = AsyncMock()
        mock_user_collection.update_one.return_value = update_result_mock
        mock_get_collection.return_value = mock_user_collection

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(f"/update_bio/{isu}", params={"bio": bio})

        assert response.status_code == 404
        assert response.json() == {"detail": "User not found or bio not updated"}


@pytest.mark.asyncio
async def test_update_username_success(app):
    isu = 123456
    username = "new_username"
    update_result_mock = AsyncMock()
    update_result_mock.modified_count = 1

    with patch.object(db_instance, "get_collection") as mock_get_collection:
        mock_user_collection = AsyncMock()
        mock_user_collection.update_one.return_value = update_result_mock
        mock_get_collection.return_value = mock_user_collection

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(f"/update_username/{isu}", params={"username": username})

        assert response.status_code == 200
        assert response.json() == {"message": "username updated successfully"}
        mock_user_collection.update_one.assert_called_once_with({"isu": isu}, {"$set": {"username": username}})


@pytest.mark.asyncio
async def test_update_username_user_not_found(app):
    isu = 123456
    username = "new_username"
    update_result_mock = AsyncMock()
    update_result_mock.modified_count = 0

    with patch.object(db_instance, "get_collection") as mock_get_collection:
        mock_user_collection = AsyncMock()
        mock_user_collection.update_one.return_value = update_result_mock
        mock_get_collection.return_value = mock_user_collection

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(f"/update_username/{isu}", params={"username": username})

        assert response.status_code == 404
        assert response.json() == {"detail": "User not found or username not updated"}
        mock_user_collection.update_one.assert_called_once_with({"isu": isu}, {"$set": {"username": username}})


@pytest.mark.asyncio
async def test_update_height_success(app):
    isu = 123456
    height = 180.5
    update_result_mock = AsyncMock()
    update_result_mock.modified_count = 1

    with patch.object(db_instance, "get_collection") as mock_get_collection:
        mock_user_collection = AsyncMock()
        mock_user_collection.update_one.return_value = update_result_mock
        mock_get_collection.return_value = mock_user_collection

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(f"/update_height/{isu}", params={"height": height})

        assert response.status_code == 200
        assert response.json() == {"message": "height updated successfully"}
        mock_user_collection.update_one.assert_called_once_with(
            {"isu": isu}, {"$set": {"mainFeatures.0.text": f"{height} cm"}}
        )


@pytest.mark.asyncio
async def test_update_height_user_not_found(app):
    isu = 123456
    height = 180.5
    update_result_mock = AsyncMock()
    update_result_mock.modified_count = 0

    with patch.object(db_instance, "get_collection") as mock_get_collection:
        mock_user_collection = AsyncMock()
        mock_user_collection.update_one.return_value = update_result_mock
        mock_get_collection.return_value = mock_user_collection

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(f"/update_height/{isu}", params={"height": height})

        assert response.status_code == 404
        assert response.json() == {"detail": "User not found or height not updated"}


@pytest.mark.asyncio
async def test_update_weight_success(app):
    isu = 123456
    weight = 75.0
    update_result_mock = AsyncMock()
    update_result_mock.modified_count = 1

    with patch.object(db_instance, "get_collection") as mock_get_collection:
        mock_user_collection = AsyncMock()
        mock_user_collection.update_one.return_value = update_result_mock
        mock_get_collection.return_value = mock_user_collection

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(f"/update_weight/{isu}", params={"weight": weight})

        assert response.status_code == 200
        assert response.json() == {"message": "weight updated successfully"}
        mock_user_collection.update_one.assert_called_once_with(
            {"isu": isu}, {"$set": {"mainFeatures.2.text": f"{weight} kg"}}
        )


@pytest.mark.asyncio
async def test_update_weight_user_not_found(app):
    isu = 123456
    weight = 75.0
    update_result_mock = AsyncMock()
    update_result_mock.modified_count = 0

    with patch.object(db_instance, "get_collection") as mock_get_collection:
        mock_user_collection = AsyncMock()
        mock_user_collection.update_one.return_value = update_result_mock
        mock_get_collection.return_value = mock_user_collection

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(f"/update_weight/{isu}", params={"weight": weight})

        assert response.status_code == 404
        assert response.json() == {"detail": "User not found or weight not updated"}


@pytest.mark.asyncio
async def test_update_zodiac_sign_success(app):
    isu = 123456
    zodiac_sign = "meow"

    with patch("app.api.profile.db_instance") as mock_db_instance:
        mock_user_collection = AsyncMock()
        mock_db_instance.get_collection.return_value = mock_user_collection
        mock_user_collection.update_one.return_value.modified_count = 1

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(f"/update_zodiac/{isu}", params={"zodiac": zodiac_sign})

        assert response.status_code == 200
        assert response.json() == {"message": "Zodiac sign updated successfully"}


@pytest.mark.asyncio
async def test_update_zodiac_sign_user_not_found(app):
    isu = 123456
    zodiac_sign = "meow"

    with patch("app.api.profile.db_instance") as mock_db_instance:
        mock_user_collection = AsyncMock()
        mock_db_instance.get_collection.return_value = mock_user_collection
        mock_user_collection.update_one.return_value.modified_count = 0

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(f"/update_zodiac/{isu}", params={"zodiac": zodiac_sign})

        assert response.status_code == 404
        assert response.json() == {"detail": "User not found or zodiac sign not updated"}


@pytest.mark.asyncio
async def test_update_tags_some_tags_do_not_exist(app):
    isu = 123456
    tags = ["507f1f77bcf86cd799439011", "507f1f77bcf86cd799439012"]
    payload = {"isu": isu, "tags": tags}

    with patch("app.api.profile.db_instance") as mock_db_instance:
        mock_user_collection = MagicMock()
        mock_tags_collection = MagicMock()

        def get_collection_mock(name):
            if name == "users":
                return mock_user_collection
            elif name == "tags":
                return mock_tags_collection
            else:
                return MagicMock()

        mock_db_instance.get_collection.side_effect = get_collection_mock

        mock_tags_collection.find.return_value.to_list = AsyncMock(
            return_value=[{"_id": ObjectId(tags[0]), "name": "existing_tag"}]
        )

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put("/update_tags", json=payload)

        assert response.status_code == 400
        assert response.json() == {"detail": "Some tags do not exist"}


@pytest.mark.asyncio
async def test_update_tags_user_not_found(app):
    isu = 123456
    tags = ["507f1f77bcf86cd799439011", "507f1f77bcf86cd799439012"]
    payload = {"isu": isu, "tags": tags}

    with patch("app.api.profile.db_instance") as mock_db_instance:
        mock_user_collection = AsyncMock()
        mock_tags_collection = MagicMock()

        def get_collection_mock(name):
            if name == "users":
                return mock_user_collection
            elif name == "tags":
                return mock_tags_collection
            else:
                return MagicMock()

        mock_db_instance.get_collection.side_effect = get_collection_mock

        existing_tags = [{"_id": ObjectId(tag_id), "name": f"tag_{tag_id}", "is_special": 0} for tag_id in tags]
        mock_tags_collection.find.return_value.to_list = AsyncMock(return_value=existing_tags)

        mock_user_collection.update_one.return_value.modified_count = 0

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put("/update_tags", json=payload)

        assert response.status_code == 404
        assert response.json() == {"detail": "User not found or tags not updated"}


@pytest.mark.asyncio
async def test_update_relationship_preferences_success(app):
    isu = 123456
    tags = ["507f1f77bcf86cd799439011", "507f1f77bcf86cd799439012"]
    payload = {"isu": isu, "tags": tags}

    with patch("app.api.profile.db_instance") as mock_db_instance:
        mock_user_collection = AsyncMock()
        mock_tags_collection = MagicMock()

        def get_collection_mock(name):
            if name == "users":
                return mock_user_collection
            elif name == "tags":
                return mock_tags_collection
            else:
                return MagicMock()

        mock_db_instance.get_collection.side_effect = get_collection_mock

        special_tags = [{"_id": ObjectId(tag_id), "name": f"special_tag_{tag_id}", "is_special": 1} for tag_id in tags]
        mock_tags_collection.find.return_value.to_list = AsyncMock(return_value=special_tags)

        mock_user_collection.update_one.return_value.modified_count = 1

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put("/update_relationship_preferences", json=payload)

        assert response.status_code == 200
        assert response.json() == {"message": "relationship preferences updated successfully"}


@pytest.mark.asyncio
async def test_update_relationship_preferences_some_tags_not_special(app):
    isu = 123456
    tags = ["507f1f77bcf86cd799439011", "507f1f77bcf86cd799439012"]
    payload = {"isu": isu, "tags": tags}

    with patch("app.api.profile.db_instance") as mock_db_instance:
        mock_user_collection = AsyncMock()
        mock_tags_collection = MagicMock()

        def get_collection_mock(name):
            if name == "users":
                return mock_user_collection
            elif name == "tags":
                return mock_tags_collection
            else:
                return MagicMock()

        mock_db_instance.get_collection.side_effect = get_collection_mock

        special_tags = [{"_id": ObjectId(tags[0]), "is_special": 1}]
        mock_tags_collection.find.return_value.to_list = AsyncMock(return_value=special_tags)

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put("/update_relationship_preferences", json=payload)

        assert response.status_code == 400
        assert response.json() == {"detail": "Some tags do not exist or are not special tags"}


@pytest.mark.asyncio
async def test_update_relationship_preferences_user_not_found(app):
    isu = 123456
    tags = ["507f1f77bcf86cd799439011", "507f1f77bcf86cd799439012"]
    payload = {"isu": isu, "tags": tags}

    with patch("app.api.profile.db_instance") as mock_db_instance:
        mock_user_collection = AsyncMock()
        mock_tags_collection = MagicMock()

        def get_collection_mock(name):
            if name == "users":
                return mock_user_collection
            elif name == "tags":
                return mock_tags_collection
            else:
                return MagicMock()

        mock_db_instance.get_collection.side_effect = get_collection_mock

        special_tags = [{"_id": ObjectId(tag_id), "name": f"special_tag_{tag_id}", "is_special": 1} for tag_id in tags]
        mock_tags_collection.find.return_value.to_list = AsyncMock(return_value=special_tags)

        mock_user_collection.update_one.return_value.modified_count = 0

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put("/update_relationship_preferences", json=payload)

        assert response.status_code == 404
        assert response.json() == {"detail": "User not found or preferences not updated"}


@pytest.mark.asyncio
async def test_update_logo_success(app):
    isu = 123456
    file_content = b"image data"
    file = BytesIO(file_content)

    with patch("app.api.profile.db_instance") as mock_db_instance, patch(
        "uuid.uuid4", return_value=uuid.UUID("12345678123456781234567812345678")
    ):
        mock_user_collection = AsyncMock()
        mock_db_instance.get_collection.return_value = mock_user_collection

        mock_db_instance.upload_file_to_minio.return_value = (
            "https://minio.example.com/logos/123_12345678123456781234567812345678.png"
        )

        mock_user_collection.update_one.return_value.modified_count = 1

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(
                f"/update_logo/{isu}",
                files={"file": ("test_image.png", file, "image/png")},
            )

        assert response.status_code == 200
        assert response.json() == {
            "message": "logo updated successfully",
            "logo_url": "https://minio.example.com/logos/123_12345678123456781234567812345678.png",
        }


@pytest.mark.asyncio
async def test_update_logo_user_not_found(app):
    isu = 123456
    file_content = b"image data"
    file = BytesIO(file_content)

    with patch("app.api.profile.db_instance") as mock_db_instance, patch(
        "uuid.uuid4", return_value=uuid.UUID("12345678123456781234567812345678")
    ):
        mock_user_collection = AsyncMock()
        mock_db_instance.get_collection.return_value = mock_user_collection

        mock_db_instance.upload_file_to_minio.return_value = (
            "https://minio.example.com/logos/123_12345678123456781234567812345678.png"
        )

        mock_user_collection.update_one.return_value.modified_count = 0

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(
                f"/update_logo/{isu}",
                files={"file": ("test_image.png", file, "image/png")},
            )

        assert response.status_code == 404
        assert response.json() == {"detail": "User not found or logo not updated"}


@pytest.mark.asyncio
async def test_get_profile_success(app):
    isu = 123456
    mock_user_id = ObjectId()
    user_data = {
        "_id": mock_user_id,
        "isu": isu,
        "logo": "bucker/some/logo.png",
        "photos": ["bucker/photo1.png", "bucker/photo2.png"],
    }

    with patch.object(db_instance, "get_collection") as mock_get_collection, patch.object(
        db_instance, "generate_presigned_url"
    ) as mock_presigned_url, patch.object(db_instance, "minio_bucket_name", new="bucker"):
        mock_user_collection = AsyncMock()
        mock_user_collection.find_one.return_value = user_data
        mock_get_collection.return_value = mock_user_collection

        mock_presigned_url.side_effect = lambda key: f"presigned/{key}"

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f"/get_profile/{isu}")

        assert response.status_code == 200
        response_json = response.json()
        assert "profile" in response_json
        assert response_json["profile"]["_id"] == str(mock_user_id)
        assert response_json["profile"]["logo"] == "presigned/some/logo.png"
        assert response_json["profile"]["photos"] == [
            "presigned/photo1.png",
            "presigned/photo2.png",
        ]
        mock_user_collection.find_one.assert_called_once_with({"isu": isu})


@pytest.mark.asyncio
async def test_get_profile_user_not_found(app):
    isu = 123456

    with patch.object(db_instance, "get_collection") as mock_get_collection:
        mock_user_collection = AsyncMock()
        mock_user_collection.find_one.return_value = None
        mock_get_collection.return_value = mock_user_collection

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f"/get_profile/{isu}")

        assert response.status_code == 404
        assert response.json() == {"detail": "User not found"}
        mock_user_collection.find_one.assert_awaited_once_with({"isu": isu})


@pytest.mark.asyncio
async def test_update_gender_preference_success(app):
    payload = {"isu": 123456, "gender_preference": "Male"}
    update_result_mock = AsyncMock()
    update_result_mock.modified_count = 1

    with patch.object(db_instance, "get_collection") as mock_get_collection:
        mock_user_collection = AsyncMock()
        mock_user_collection.update_one.return_value = update_result_mock
        mock_get_collection.return_value = mock_user_collection

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put("/update_gender_preference", json=payload)

        assert response.status_code == 200
        assert response.json() == {"message": "gender preference updated successfully"}
        mock_user_collection.update_one.assert_called_once_with(
            {"isu": payload["isu"]},
            {
                "$set": {
                    "gender_preferences": [
                        {
                            "text": payload["gender_preference"],
                            "icon": "gender_preferences",
                        }
                    ]
                }
            },
        )


@pytest.mark.asyncio
async def test_update_gender_preference_user_not_found(app):
    payload = {"isu": 123456, "gender_preference": "Male"}
    update_result_mock = AsyncMock()
    update_result_mock.modified_count = 0

    with patch.object(db_instance, "get_collection") as mock_get_collection:
        mock_user_collection = AsyncMock()
        mock_user_collection.update_one.return_value = update_result_mock
        mock_get_collection.return_value = mock_user_collection

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put("/update_gender_preference", json=payload)

        assert response.status_code == 404
        assert response.json() == {"detail": "User not found or gender preference not updated"}
        mock_user_collection.update_one.assert_called_once_with(
            {"isu": payload["isu"]},
            {
                "$set": {
                    "gender_preferences": [
                        {
                            "text": payload["gender_preference"],
                            "icon": "gender_preferences",
                        }
                    ]
                }
            },
        )


@pytest.mark.asyncio
async def test_update_carousel_photo_success(app):
    isu = 123456
    old_photo_url = "old_photo.png"
    new_file_content = b"new image data"
    new_file = BytesIO(new_file_content)
    new_file.filename = "new_photo.png"
    new_file.content_type = "image/png"
    new_file_extension = "png"
    new_file_uuid = "12345678123456781234567812345678"
    new_file_name = f"carousel/{isu}_{new_file_uuid}.{new_file_extension}"
    new_file_url = f"bucket/{new_file_name}"

    user_data = {
        "isu": isu,
        "photos": [old_photo_url, "another_photo.png"],
    }

    with patch("app.api.profile.db_instance") as mock_db_instance, patch(
        "uuid.uuid4", return_value=uuid.UUID(new_file_uuid)
    ):
        mock_user_collection = AsyncMock()
        mock_db_instance.get_collection.return_value = mock_user_collection

        mock_user_collection.find_one.return_value = user_data

        mock_db_instance.minio_instance.remove_object.return_value = None
        mock_db_instance.upload_file_to_minio.return_value = new_file_url

        mock_user_collection.update_one.return_value.modified_count = 1

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(
                f"/update_carousel_photo/{isu}",
                params={"old_photo_url": old_photo_url},
                files={"new_file": (new_file.filename, new_file, new_file.content_type)},
            )

        assert response.status_code == 200
        assert response.json() == {
            "message": "carousel photo updated successfully",
            "new_photo_url": new_file_url,
        }
        mock_db_instance.minio_instance.remove_object.assert_called_once_with(
            mock_db_instance.minio_bucket_name, old_photo_url
        )
        mock_db_instance.upload_file_to_minio.assert_called_once()
        mock_user_collection.update_one.assert_called_once()


@pytest.mark.asyncio
async def test_update_carousel_photo_user_not_found(app):
    isu = 123456
    old_photo_url = "old_photo.png"
    new_file_content = b"new image data"
    new_file = BytesIO(new_file_content)
    new_file.filename = "new_photo.png"
    new_file.content_type = "image/png"

    with patch("app.api.profile.db_instance") as mock_db_instance:
        mock_user_collection = AsyncMock()
        mock_db_instance.get_collection.return_value = mock_user_collection

        mock_user_collection.find_one.return_value = None

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(
                f"/update_carousel_photo/{isu}",
                params={"old_photo_url": old_photo_url},
                files={"new_file": (new_file.filename, new_file, new_file.content_type)},
            )

        assert response.status_code == 404
        assert response.json() == {"detail": "User not found"}


@pytest.mark.asyncio
async def test_update_carousel_photo_old_photo_not_found(app):
    isu = 123456
    old_photo_url = "non_existing_photo.png"
    new_file_content = b"new image data"
    new_file = BytesIO(new_file_content)
    new_file.filename = "new_photo.png"
    new_file.content_type = "image/png"

    user_data = {"isu": isu, "photos": {"carousel": ["photo1.png", "photo2.png"]}}

    with patch("app.api.profile.db_instance") as mock_db_instance:
        mock_user_collection = AsyncMock()
        mock_db_instance.get_collection.return_value = mock_user_collection

        mock_user_collection.find_one.return_value = user_data

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(
                f"/update_carousel_photo/{isu}",
                params={"old_photo_url": old_photo_url},
                files={"new_file": (new_file.filename, new_file, new_file.content_type)},
            )

        assert response.status_code == 404
        assert response.json() == {"detail": "Photo not found in carousel"}


@pytest.mark.asyncio
async def test_delete_carousel_photo_success(app):
    isu = 123456
    photo_url = "photo_to_delete.png"

    user_data = {"isu": isu, "photos": ["photo_to_delete.png", "another_photo.png"]}

    with patch("app.api.profile.db_instance") as mock_db_instance:
        mock_user_collection = AsyncMock()
        mock_db_instance.get_collection.return_value = mock_user_collection

        mock_user_collection.find_one.return_value = user_data

        mock_db_instance.minio_instance.remove_object.return_value = None

        mock_user_collection.update_one.return_value.modified_count = 1

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.delete(f"/delete_carousel_photo/{isu}", params={"photo_url": photo_url})

        assert response.status_code == 200
        assert response.json() == {"message": "carousel photo deleted successfully"}
        mock_db_instance.minio_instance.remove_object.assert_called_once_with(
            mock_db_instance.minio_bucket_name, photo_url
        )
        mock_user_collection.update_one.assert_called_once()


@pytest.mark.asyncio
async def test_delete_carousel_photo_user_not_found(app):
    isu = 123456
    photo_url = "photo_to_delete.png"

    with patch("app.api.profile.db_instance") as mock_db_instance:
        mock_user_collection = AsyncMock()
        mock_db_instance.get_collection.return_value = mock_user_collection

        mock_user_collection.find_one.return_value = None

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.delete(f"/delete_carousel_photo/{isu}", params={"photo_url": photo_url})

        assert response.status_code == 404
        assert response.json() == {"detail": "User not found"}


@pytest.mark.asyncio
async def test_delete_carousel_photo_photo_not_found(app):
    isu = 123456
    photo_url = "non_existing_photo.png"

    user_data = {"isu": isu, "photos": {"carousel": ["photo1.png", "photo2.png"]}}

    with patch("app.api.profile.db_instance") as mock_db_instance:
        mock_user_collection = AsyncMock()
        mock_db_instance.get_collection.return_value = mock_user_collection

        mock_user_collection.find_one.return_value = user_data

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.delete(f"/delete_carousel_photo/{isu}", params={"photo_url": photo_url})

        assert response.status_code == 404
        assert response.json() == {"detail": "Photo not found in carousel"}


@pytest.mark.asyncio
async def test_update_worldview_success(app):
    isu = 123456
    worldview = "worldview"
    update_result_mock = AsyncMock()
    update_result_mock.modified_count = 1

    with patch.object(db_instance, "get_collection") as mock_get_collection:
        mock_user_collection = AsyncMock()
        mock_user_collection.update_one.return_value = update_result_mock
        mock_get_collection.return_value = mock_user_collection

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(f"/update_worldview/{isu}", params={"worldview": worldview})

        assert response.status_code == 200
        assert response.json() == {"message": "worldview updated successfully"}
        mock_user_collection.update_one.assert_called_once_with(
            {"isu": isu}, {"$set": {"mainFeatures.5.text": worldview}}
        )


@pytest.mark.asyncio
async def test_update_worldview_user_not_found(app):
    isu = 123456
    worldview = "worldview"
    update_result_mock = AsyncMock()
    update_result_mock.modified_count = 0

    with patch.object(db_instance, "get_collection") as mock_get_collection:
        mock_user_collection = AsyncMock()
        mock_user_collection.update_one.return_value = update_result_mock
        mock_get_collection.return_value = mock_user_collection

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(f"/update_worldview/{isu}", params={"worldview": worldview})

        assert response.status_code == 404
        assert response.json() == {"detail": "User not found or worldview not updated"}
        mock_user_collection.update_one.assert_called_once_with(
            {"isu": isu}, {"$set": {"mainFeatures.5.text": worldview}}
        )


@pytest.mark.asyncio
async def test_update_children_success(app):
    isu = 123456
    children = "children"
    update_result_mock = AsyncMock()
    update_result_mock.modified_count = 1

    with patch.object(db_instance, "get_collection") as mock_get_collection:
        mock_user_collection = AsyncMock()
        mock_user_collection.update_one.return_value = update_result_mock
        mock_get_collection.return_value = mock_user_collection

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(f"/update_children/{isu}", params={"children": children})

        assert response.status_code == 200
        assert response.json() == {"message": "children updated successfully"}
        mock_user_collection.update_one.assert_called_once_with(
            {"isu": isu}, {"$set": {"mainFeatures.6.text": children}}
        )


@pytest.mark.asyncio
async def test_update_children_user_not_found(app):
    isu = 123456
    children = "children"
    update_result_mock = AsyncMock()
    update_result_mock.modified_count = 0

    with patch.object(db_instance, "get_collection") as mock_get_collection:
        mock_user_collection = AsyncMock()
        mock_user_collection.update_one.return_value = update_result_mock
        mock_get_collection.return_value = mock_user_collection

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(f"/update_children/{isu}", params={"children": children})

        assert response.status_code == 404
        assert response.json() == {"detail": "User not found or children not updated"}
        mock_user_collection.update_one.assert_called_once_with(
            {"isu": isu}, {"$set": {"mainFeatures.6.text": children}}
        )


@pytest.mark.asyncio
async def test_update_languages_success(app):
    payload = {"isu": 123456, "languages": ["English", "Russian"]}
    update_result_mock = AsyncMock()
    update_result_mock.modified_count = 1

    with patch.object(db_instance, "get_collection") as mock_get_collection:
        mock_user_collection = AsyncMock()
        mock_user_collection.update_one.return_value = update_result_mock
        mock_get_collection.return_value = mock_user_collection

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put("/update_languages", json=payload)

        assert response.status_code == 200
        assert response.json() == {"message": "languages updated successfully"}
        mock_user_collection.update_one.assert_called_once()
        mock_user_collection.update_one.assert_called_with(
            {"isu": payload["isu"]},
            {
                "$set": {
                    "mainFeatures.7": [
                        {"text": "English", "icon": "languages"},
                        {"text": "Russian", "icon": "languages"},
                    ]
                }
            },
        )


@pytest.mark.asyncio
async def test_update_languages_user_not_found(app):
    payload = {"isu": 123456, "languages": ["English", "Russian"]}
    update_result_mock = AsyncMock()
    update_result_mock.modified_count = 0

    with patch.object(db_instance, "get_collection") as mock_get_collection:
        mock_user_collection = AsyncMock()
        mock_user_collection.update_one.return_value = update_result_mock
        mock_get_collection.return_value = mock_user_collection

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put("/update_languages", json=payload)

        assert response.status_code == 404
        assert response.json() == {"detail": "User not found or languages not updated"}
        mock_user_collection.update_one.assert_called_once()


@pytest.mark.asyncio
async def test_update_alcohol_success(app):
    isu = 123456
    alcohol = "Negative"
    update_result_mock = AsyncMock()
    update_result_mock.modified_count = 1

    with patch.object(db_instance, "get_collection") as mock_get_collection:
        mock_user_collection = AsyncMock()
        mock_user_collection.update_one.return_value = update_result_mock
        mock_get_collection.return_value = mock_user_collection

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(f"/update_alcohol/{isu}", params={"alcohol": alcohol})

        assert response.status_code == 200
        assert response.json() == {"message": "alcohol updated successfully"}
        mock_user_collection.update_one.assert_called_once_with(
            {"isu": isu}, {"$set": {"mainFeatures.8.text": alcohol}}
        )


@pytest.mark.asyncio
async def test_update_alcohol_user_not_found(app):
    isu = 123456
    alcohol = "Negative"
    update_result_mock = AsyncMock()
    update_result_mock.modified_count = 0

    with patch.object(db_instance, "get_collection") as mock_get_collection:
        mock_user_collection = AsyncMock()
        mock_user_collection.update_one.return_value = update_result_mock
        mock_get_collection.return_value = mock_user_collection

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(f"/update_alcohol/{isu}", params={"alcohol": alcohol})

        assert response.status_code == 404
        assert response.json() == {"detail": "User not found or alcohol not updated"}
        mock_user_collection.update_one.assert_called_once()


@pytest.mark.asyncio
async def test_update_smoking_success(app):
    isu = 123456
    smoking = "Negative"
    update_result_mock = AsyncMock()
    update_result_mock.modified_count = 1

    with patch.object(db_instance, "get_collection") as mock_get_collection:
        mock_user_collection = AsyncMock()
        mock_user_collection.update_one.return_value = update_result_mock
        mock_get_collection.return_value = mock_user_collection

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(f"/update_smoking/{isu}", params={"smoking": smoking})

        assert response.status_code == 200
        assert response.json() == {"message": "Smoking updated successfully"}
        mock_user_collection.update_one.assert_called_once_with(
            {"isu": isu}, {"$set": {"mainFeatures.9.text": smoking}}
        )


@pytest.mark.asyncio
async def test_update_smoking_user_not_found(app):
    isu = 123456
    smoking = "Negative"
    update_result_mock = AsyncMock()
    update_result_mock.modified_count = 0

    with patch.object(db_instance, "get_collection") as mock_get_collection:
        mock_user_collection = AsyncMock()
        mock_user_collection.update_one.return_value = update_result_mock
        mock_get_collection.return_value = mock_user_collection

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(f"/update_smoking/{isu}", params={"smoking": smoking})

        assert response.status_code == 404
        assert response.json() == {"detail": "User not found or smoking not updated"}
        mock_user_collection.update_one.assert_called_once()
