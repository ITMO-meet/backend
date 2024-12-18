import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock, patch
from app.utils.db import db_instance
from app.api.matches import router


@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.mark.asyncio
async def test_get_random_person_success(app):
    user_id = 123456
    mock_person = {
        "isu": 654321,
        "username": "John Doe",
        "bio": "A random person",
        "logo": "https://example.com/image.png",
        "photos": [],
        "mainFeatures": [],
        "interests": [],
        "itmo": [],
        "gender_preferences": [],
        "relationship_preferences": [],
        "isStudent": True,
    }

    with patch.object(db_instance, "get_random_person", AsyncMock(return_value=mock_person)):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/random_person", params={"user_id": user_id})

        assert response.status_code == 200
        assert response.json() == mock_person


@pytest.mark.asyncio
async def test_get_random_person_no_person_available(app):
    user_id = 123456

    with patch.object(db_instance, "get_random_person", AsyncMock(return_value=None)):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/random_person", params={"user_id": user_id})

        assert response.status_code == 404
        assert response.json() == {"detail": "No more persons available"}


@pytest.mark.asyncio
async def test_like_person_success(app):
    payload = {"user_id": 123456, "target_id": 654321}
    mock_result = {"matched": False, "chat_id": None}

    with patch.object(db_instance, "like_user", AsyncMock(return_value=mock_result)):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/like_person", json=payload)

        assert response.status_code == 200
        assert response.json() == {
            "message": "person liked successfully",
            "matched": False,
        }


@pytest.mark.asyncio
async def test_dislike_person_success(app):
    payload = {"user_id": 123456, "target_id": 654321}

    with patch.object(db_instance, "dislike_user", AsyncMock(return_value=None)):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/dislike_person", json=payload)

        assert response.status_code == 200
        assert response.json() == {"message": "person disliked successfully"}


@pytest.mark.asyncio
async def test_get_matches_success(app):
    isu = 123456
    mock_likes = [{"user_id": 654321}]
    mock_users = [
        {
            "isu": 654321,
            "username": "Jane Doe",
            "bio": "A match",
            "logo": "https://example.com/logo.png",
            "photos": [],
            "mainFeatures": [],
            "interests": [],
            "itmo": [],
            "gender_preferences": [],
            "relationship_preferences": [],
            "isStudent": True,
        }
    ]

    mock_likes_cursor = AsyncMock()
    mock_likes_cursor.to_list.return_value = mock_likes

    mock_users_cursor = AsyncMock()
    mock_users_cursor.to_list.return_value = mock_users

    mock_likes_collection = MagicMock()
    mock_likes_collection.find.return_value = mock_likes_cursor

    mock_users_collection = MagicMock()
    mock_users_collection.find.return_value = mock_users_cursor

    mock_db = MagicMock()
    mock_db.__getitem__.side_effect = lambda name: {
        "likes": mock_likes_collection,
        "users": mock_users_collection,
    }[name]

    with patch.object(db_instance, "db", mock_db):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/liked_me", params={"isu": isu})

        assert response.status_code == 200
        assert response.json() == mock_users
