import pytest
from fastapi import FastAPI
import uuid
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch, MagicMock
from app.utils.db import db_instance
from app.api.profile import router
from io import BytesIO
from bson import ObjectId


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
        mock_user_collection.update_one.assert_called_once_with(
            {"isu": isu}, {"$set": {"bio": bio}}
        )


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
    payload = {"isu": 123456, "username": "new_username"}
    update_result_mock = AsyncMock()
    update_result_mock.modified_count = 1

    with patch.object(db_instance, "get_collection") as mock_get_collection:
        mock_user_collection = AsyncMock()
        mock_user_collection.update_one.return_value = update_result_mock
        mock_get_collection.return_value = mock_user_collection

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put("/update_username", json=payload)

        assert response.status_code == 200
        assert response.json() == {"message": "username updated successfully"}
        mock_user_collection.update_one.assert_called_once_with(
            {"isu": payload["isu"]}, {"$set": {"username": payload["username"]}}
        )


@pytest.mark.asyncio
async def test_update_username_user_not_found(app):
    payload = {"isu": 123456, "username": "new_username"}
    update_result_mock = AsyncMock()
    update_result_mock.modified_count = 0

    with patch.object(db_instance, "get_collection") as mock_get_collection:
        mock_user_collection = AsyncMock()
        mock_user_collection.update_one.return_value = update_result_mock
        mock_get_collection.return_value = mock_user_collection

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put("/update_username", json=payload)

        assert response.status_code == 404
        assert response.json() == {"detail": "User not found or username not updated"}


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
            {"isu": isu}, {"$set": {"person_params.height": height}}
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
            {"isu": isu}, {"$set": {"person_params.weight": weight}}
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
            response = await ac.put(
                f"/update_zodiac/{isu}", params={"zodiac_sign": zodiac_sign}
            )

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
            response = await ac.put(
                f"/update_zodiac/{isu}", params={"zodiac_sign": zodiac_sign}
            )

        assert response.status_code == 404
        assert response.json() == {
            "detail": "User not found or zodiac sign not updated"
        }


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

        existing_tags = [
            {"_id": ObjectId(tag_id), "name": f"tag_{tag_id}"} for tag_id in tags
        ]
        mock_tags_collection.find.return_value.to_list = AsyncMock(
            return_value=existing_tags
        )

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

        special_tags = [{"_id": ObjectId(tag_id), "is_special": 1} for tag_id in tags]
        mock_tags_collection.find.return_value.to_list = AsyncMock(
            return_value=special_tags
        )

        mock_user_collection.update_one.return_value.modified_count = 1

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put("/update_relationship_preferences", json=payload)

        assert response.status_code == 200
        assert response.json() == {
            "message": "relationship preferences updated successfully"
        }


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
        mock_tags_collection.find.return_value.to_list = AsyncMock(
            return_value=special_tags
        )

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put("/update_relationship_preferences", json=payload)

        assert response.status_code == 400
        assert response.json() == {
            "detail": "Some tags do not exist or are not special tags"
        }


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

        special_tags = [{"_id": ObjectId(tag_id), "is_special": 1} for tag_id in tags]
        mock_tags_collection.find.return_value.to_list = AsyncMock(
            return_value=special_tags
        )

        mock_user_collection.update_one.return_value.modified_count = 0

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put("/update_relationship_preferences", json=payload)

        assert response.status_code == 404
        assert response.json() == {
            "detail": "User not found or preferences not updated"
        }


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
