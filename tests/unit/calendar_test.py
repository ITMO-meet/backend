import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from unittest.mock import patch
from app.utils.db import db_instance
from app.api.calendar import router

@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(router)
    return app

@pytest.mark.asyncio
async def test_get_calendar_success(app):
    isu=123456
    mock_schedule_data = {"data": {"1": {"9:00": "something1"}, "2": {"10:00": "something2"}}}

    with patch.object(db_instance, "get_json_from_minio", return_value=mock_schedule_data) as mock_db_call:
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f"/get_calendar/{isu}")

        mock_db_call.assert_called_once_with(f"schedule_{isu}.json")

        assert response.status_code == 200
        assert response.json() == mock_schedule_data["data"]

@pytest.mark.asyncio
async def test_get_calendar_not_found(app):
    isu=123456
    error_message = "Nothing found lol"

    with patch.object(db_instance, "get_json_from_minio", side_effect=ValueError(error_message)):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f"/get_calendar/{isu}")

        assert response.status_code == 404
        assert f"Schedule not found: {error_message}" in response.json()["detail"]