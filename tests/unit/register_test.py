import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch, MagicMock
from app.main import app
from app.utils.db import db_instance
import os

os.environ['TESTING'] = 'True'

@pytest.mark.asyncio
async def test_select_tags_success():
    mock_tags_collection = MagicMock()
    mock_users_collection = AsyncMock()

    with patch.object(
        db_instance,
        "get_collection",
        side_effect=lambda name: (
            mock_tags_collection if name == "tags" else mock_users_collection
        ),
    ):
        mock_cursor = MagicMock()
        mock_cursor.to_list = AsyncMock(
            return_value=[
                {"_id": "tag1", "name": "Tag1"},
                {"_id": "tag2", "name": "Tag2"},
            ]
        )
        mock_tags_collection.find.return_value = mock_cursor

        mock_users_collection.update_one.return_value.modified_count = 1

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(
                "/auth/register/select_tags",
                json={"isu": 12345, "tags": ["Tag1", "Tag2"]},
            )
    assert response.status_code == 200
    assert response.json() == {
        "message": "Tags selected successfully, proceed to the next step"
    }


@pytest.mark.asyncio
async def test_select_tags_not_found():
    mock_tags_collection = MagicMock()
    mock_users_collection = AsyncMock()

    with patch.object(
        db_instance,
        "get_collection",
        side_effect=lambda name: (
            mock_tags_collection if name == "tags" else mock_users_collection
        ),
    ):
        mock_cursor = MagicMock()
        mock_cursor.to_list = AsyncMock(return_value=[])
        mock_tags_collection.find.return_value = mock_cursor

        mock_users_collection.update_one = AsyncMock()

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(
                "/auth/register/select_tags",
                json={"isu": 12345, "tags": ["NonExistingTag"]},
            )

    assert response.status_code == 404
    assert response.json() == {"detail": "Tags not found"}


@pytest.mark.asyncio
async def test_add_profile_details_success():
    mock_users_collection = AsyncMock()

    with patch.object(
        db_instance, "get_collection", return_value=mock_users_collection
    ):
        mock_update_result = MagicMock()
        mock_update_result.modified_count = 1
        mock_users_collection.update_one.return_value = mock_update_result

        payload = {
            "isu": 123456,
            "bio": "test_bio",
            "weight": 420,
            "height": 69,
            "hair_color": "brown",
            "zodiac_sign": "test_sign",
        }

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/auth/register/profile_details", json=payload)

        assert response.status_code == 200
        assert response.json() == {"message": "Profile details updated successfully"}


@pytest.mark.asyncio
async def test_add_profile_details_user_not_found():
    mock_users_collection = AsyncMock()

    with patch.object(
        db_instance, "get_collection", return_value=mock_users_collection
    ):
        mock_update_result = MagicMock()
        mock_update_result.modified_count = 0
        mock_users_collection.update_one.return_value = mock_update_result

        payload = {
            "isu": 123456,
            "bio": "test_bio",
            "weight": 420,
            "height": 69,
            "hair_color": "brown",
            "zodiac_sign": "test_sign",
        }

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/auth/register/profile_details", json=payload)

        assert response.status_code == 404
        assert response.json() == {"detail": "User not found or profile not updated"}


@pytest.mark.asyncio
async def test_upload_logo_success():
    mock_users_collection = AsyncMock()

    with patch.object(
        db_instance, "get_collection", return_value=mock_users_collection
    ):
        with patch.object(
            db_instance,
            "upload_file_to_minio",
            return_value="http://minio.test/logos/logo.jpg",
        ):
            mock_update_result = MagicMock()
            mock_update_result.modified_count = 1
            mock_users_collection.update_one.return_value = mock_update_result

            async with AsyncClient(app=app, base_url="http://test") as ac:
                files = {"file": ("logo.jpg", b"fake image data", "image/jpeg")}
                params = {"isu": 123456}
                response = await ac.post(
                    "/auth/register/upload_logo", params=params, files=files
                )

            assert response.status_code == 200
            assert response.json() == {
                "message": "Avatar uploaded successfully",
                "avatar_url": "http://minio.test/logos/logo.jpg",
            }


@pytest.mark.asyncio
async def test_upload_logo_user_not_found():
    mock_users_collection = AsyncMock()

    with patch.object(
        db_instance, "get_collection", return_value=mock_users_collection
    ):
        with patch.object(
            db_instance,
            "upload_file_to_minio",
            return_value="http://minio.test/logos/logo.jpg",
        ):
            mock_update_result = MagicMock()
            mock_update_result.modified_count = 0
            mock_users_collection.update_one.return_value = mock_update_result

            async with AsyncClient(app=app, base_url="http://test") as ac:
                files = {"file": ("logo.jpg", b"fake image data", "image/jpeg")}
                params = {"isu": 123456}
                response = await ac.post(
                    "/auth/register/upload_logo", params=params, files=files
                )

            assert response.status_code == 404
            assert response.json() == {"detail": "User not found or logo not uploaded"}


@pytest.mark.asyncio
async def test_upload_carousel_success():
    mock_users_collection = AsyncMock()

    with patch.object(
        db_instance, "get_collection", return_value=mock_users_collection
    ):
        with patch.object(db_instance, "upload_file_to_minio") as mock_upload:
            mock_file_urls = [
                "http://minio.test/carousel/image1.jpg",
                "http://minio.test/carousel/image2.jpg",
                "http://minio.test/carousel/image3.jpg",
            ]
            mock_upload.side_effect = mock_file_urls

            mock_update_result = MagicMock()
            mock_update_result.modified_count = 1
            mock_users_collection.update_one.return_value = mock_update_result

            async with AsyncClient(app=app, base_url="http://test") as ac:
                files = [
                    ("files", ("image1.jpg", b"fake image data 1", "image/jpeg")),
                    ("files", ("image2.jpg", b"fake image data 2", "image/jpeg")),
                    ("files", ("image3.jpg", b"fake image data 3", "image/jpeg")),
                ]
                params = {"isu": 123456}
                response = await ac.post(
                    "/auth/register/upload_carousel", params=params, files=files
                )

            assert response.status_code == 200
            assert response.json() == {
                "message": "Carousel photos uploaded successfully",
                "carousel_urls": mock_file_urls,
            }

            assert mock_upload.call_count == 3


@pytest.mark.asyncio
async def test_upload_carousel_user_not_found():
    mock_users_collection = AsyncMock()

    with patch.object(
        db_instance, "get_collection", return_value=mock_users_collection
    ):
        with patch.object(db_instance, "upload_file_to_minio") as mock_upload:
            mock_file_urls = [
                "http://minio.test/carousel/image1.jpg",
                "http://minio.test/carousel/image2.jpg",
                "http://minio.test/carousel/image3.jpg",
            ]
            mock_upload.side_effect = mock_file_urls

            mock_update_result = MagicMock()
            mock_update_result.modified_count = 0
            mock_users_collection.update_one.return_value = mock_update_result

            async with AsyncClient(app=app, base_url="http://test") as ac:
                files = [
                    ("files", ("image1.jpg", b"fake image data 1", "image/jpeg")),
                    ("files", ("image2.jpg", b"fake image data 2", "image/jpeg")),
                    ("files", ("image3.jpg", b"fake image data 3", "image/jpeg")),
                ]
                params = {"isu": 123456}
                response = await ac.post(
                    "/auth/register/upload_carousel", params=params, files=files
                )

            assert response.status_code == 404
            assert response.json() == {
                "detail": "User not found or carousel photos not updated"
            }


@pytest.mark.asyncio
async def test_select_username_success():
    payload = {"isu": 123456, "username": "new_username"}
    update_result_mock = AsyncMock()
    update_result_mock.modified_count = 1

    with patch.object(db_instance, "get_collection") as mock_get_collection:
        mock_user_collection = AsyncMock()
        mock_user_collection.update_one.return_value = update_result_mock
        mock_get_collection.return_value = mock_user_collection

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/auth/register/select_username", json=payload)

        assert response.status_code == 200
        assert response.json() == {"message": "Username updated successfully"}
        mock_user_collection.update_one.assert_called_once_with(
            {"isu": payload["isu"]}, {"$set": {"username": payload["username"]}}
        )


@pytest.mark.asyncio
async def test_select_username_user_not_found():
    payload = {"isu": 123456, "username": "new_username"}
    update_result_mock = AsyncMock()
    update_result_mock.modified_count = 0

    with patch.object(db_instance, "get_collection") as mock_get_collection:
        mock_user_collection = AsyncMock()
        mock_user_collection.update_one.return_value = update_result_mock
        mock_get_collection.return_value = mock_user_collection

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/auth/register/select_username", json=payload)

        assert response.status_code == 404
        assert response.json() == {"detail": "User not found or username not updated"}
        mock_user_collection.update_one.assert_called_once_with(
            {"isu": payload["isu"]}, {"$set": {"username": payload["username"]}}
        )


@pytest.mark.asyncio
async def test_select_preferences_success():
    payload = {"isu": 123456, "gender_preference": "Female"}
    update_result_mock = AsyncMock()
    update_result_mock.modified_count = 1

    with patch.object(db_instance, "get_collection") as mock_get_collection:
        mock_user_collection = AsyncMock()
        mock_user_collection.update_one.return_value = update_result_mock
        mock_get_collection.return_value = mock_user_collection

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/auth/register/select_preferences", json=payload)

        assert response.status_code == 200
        assert response.json() == {"message": "Gender preference updated successfully"}
        mock_user_collection.update_one.assert_called_once_with(
            {"isu": payload["isu"]},
            {"$set": {"preferences.gender_preference": payload["gender_preference"]}},
        )


@pytest.mark.asyncio
async def test_select_preferences_user_not_found():
    payload = {"isu": 123456, "gender_preference": "Female"}
    update_result_mock = AsyncMock()
    update_result_mock.modified_count = 0

    with patch.object(db_instance, "get_collection") as mock_get_collection:
        mock_user_collection = AsyncMock()
        mock_user_collection.update_one.return_value = update_result_mock
        mock_get_collection.return_value = mock_user_collection

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/auth/register/select_preferences", json=payload)

        assert response.status_code == 404
        assert response.json() == {"detail": "User not found or preference not updated"}
        mock_user_collection.update_one.assert_called_once_with(
            {"isu": payload["isu"]},
            {"$set": {"preferences.gender_preference": payload["gender_preference"]}},
        )


@pytest.mark.asyncio
async def test_select_tags_user_not_found():
    mock_tags_collection = MagicMock()
    mock_users_collection = AsyncMock()

    with patch.object(
        db_instance,
        "get_collection",
        side_effect=lambda name: (
            mock_tags_collection if name == "tags" else mock_users_collection
        ),
    ):
        mock_cursor = MagicMock()
        mock_cursor.to_list = AsyncMock(
            return_value=[
                {"_id": "tag1", "name": "Tag1"},
                {"_id": "tag2", "name": "Tag2"},
            ]
        )
        mock_tags_collection.find.return_value = mock_cursor

        mock_users_collection.update_one.return_value.modified_count = 0

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(
                "/auth/register/select_tags",
                json={"isu": 12345, "tags": ["Tag1", "Tag2"]},
            )
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found or tags not updated"}
