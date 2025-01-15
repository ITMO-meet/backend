import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from unittest.mock import AsyncMock, MagicMock, patch
from app.api.stories import (
    router,
)
from app.utils.db import db_instance
from bson import ObjectId
from datetime import datetime, timedelta


@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(router)
    return app


# create_story
@pytest.mark.asyncio
async def test_create_story_success(app):
    isu = 123456

    with patch.object(
        db_instance, "get_collection"
    ) as mock_get_collection, patch.object(
        db_instance, "upload_file_to_minio", new_callable=AsyncMock
    ) as mock_upload_file:
        mock_stories_coll = MagicMock()
        mock_get_collection.return_value = mock_stories_coll

        mock_upload_file.return_value = "http://minio.test/stories/test.jpg"

        mock_insert_res = MagicMock()
        mock_insert_res.inserted_id = ObjectId()
        mock_stories_coll.insert_one = AsyncMock(return_value=mock_insert_res)

        async with AsyncClient(app=app, base_url="http://test") as ac:
            files = {"file": ("test.jpg", b"random img data", "image/jpeg")}
            params = {"isu": isu}
            response = await ac.post("/create_story", params=params, files=files)

        assert response.status_code == 200
        response_json = response.json()
        assert "expDate" in response_json
        assert "id" in response_json

        mock_upload_file.assert_called_once()
        mock_stories_coll.insert_one.assert_called_once()


@pytest.mark.asyncio
async def test_create_story_failure(app):
    isu = 123456

    with patch.object(
        db_instance, "get_collection"
    ) as mock_get_collection, patch.object(
        db_instance, "upload_file_to_minio", new_callable=AsyncMock
    ) as mock_upload_file_to_minio:
        mock_stories_collection = MagicMock()
        mock_get_collection.return_value = mock_stories_collection

        mock_upload_file_to_minio.return_value = "http://minio.test/stories/test.jpg"

        mock_insert_res = MagicMock()
        mock_insert_res.inserted_id = None
        mock_stories_collection.insert_one = AsyncMock(return_value=mock_insert_res)

        async with AsyncClient(app=app, base_url="http://test") as ac:
            files = {"file": ("test.jpg", b"random img data", "image/jpeg")}
            params = {"isu": isu}
            response = await ac.post("/create_story", params=params, files=files)

        assert response.status_code == 404
        assert response.json() == {"detail": "Story cannot be inserted"}


# get story
@pytest.mark.asyncio
async def test_get_story_success(app):
    story_id = str(ObjectId())
    story_data = {
        "_id": ObjectId(story_id),
        "isu": 654321,
        "url": "http://minio.test/stories/story.jpg",
        "expiration_date": int((datetime.now() + timedelta(hours=24)).timestamp()),
    }

    with patch.object(
        db_instance, "get_collection"
    ) as mock_get_collection, patch.object(
        db_instance, "generate_presigned_url"
    ) as mock_generate_presigned_url:
        mock_stories_collection = AsyncMock()
        mock_get_collection.return_value = mock_stories_collection

        mock_stories_collection.find_one.return_value = story_data
        mock_generate_presigned_url.return_value = story_data["url"]

        async with AsyncClient(app=app, base_url="http://test") as ac:
            params = {"isu_from": 0, "isu_whose": 0, "story_id": story_id}
            response = await ac.get("/get_story", params=params)

        assert response.status_code == 200
        assert response.json() == {
            "id": story_id,
            "isu": story_data["isu"],
            "url": story_data["url"],
            "expiration_date": story_data["expiration_date"],
        }
        mock_stories_collection.find_one.assert_called_once_with(
            {"_id": ObjectId(story_id)}
        )


@pytest.mark.asyncio
async def test_get_story_not_found(app):
    story_id = str(ObjectId())

    with patch.object(db_instance, "get_collection") as mock_get_collection:
        mock_stories_collection = AsyncMock()
        mock_get_collection.return_value = mock_stories_collection

        mock_stories_collection.find_one.return_value = None

        async with AsyncClient(app=app, base_url="http://test") as ac:
            params = {"isu_from": 0, "isu_whose": 0, "story_id": story_id}
            response = await ac.get("/get_story", params=params)

        assert response.status_code == 404
        assert response.json() == {"detail": "Story not found"}
        mock_stories_collection.find_one.assert_called_once_with(
            {"_id": ObjectId(story_id)}
        )


@pytest.mark.asyncio
async def test_get_user_stories_success(app):
    isu = 123456
    stories_data = [
        {"_id": ObjectId(), "isu": isu},
        {"_id": ObjectId(), "isu": isu},
    ]
    with patch.object(db_instance, "get_collection") as mock_get_collection:
        mock_stories_collection = MagicMock()
        mock_get_collection.return_value = mock_stories_collection

        mock_cursor = MagicMock()
        mock_cursor.to_list = AsyncMock(return_value=stories_data)
        mock_stories_collection.find.return_value = mock_cursor

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f"/get_user_stories/{isu}")

        assert response.status_code == 200
        assert response.json() == {
            "stories": [str(story["_id"]) for story in stories_data]
        }
        mock_stories_collection.find.assert_called_once_with({"isu": isu})


@pytest.mark.asyncio
async def test_get_user_stories_no_stories(app):
    isu = 123456
    with patch.object(db_instance, "get_collection") as mock_get_collection:
        mock_stories_collection = MagicMock()
        mock_get_collection.return_value = mock_stories_collection

        mock_cursor = MagicMock()
        mock_cursor.to_list = AsyncMock(return_value=[])
        mock_stories_collection.find.return_value = mock_cursor

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f"/get_user_stories/{isu}")

        assert response.status_code == 404
        assert response.json() == {"detail": "User has no stories"}
        mock_stories_collection.find.assert_called_once_with({"isu": isu})
