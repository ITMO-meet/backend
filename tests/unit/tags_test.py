import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock
from app.main import app
from app.utils.db import db_instance


@pytest.mark.asyncio
async def test_get_tags():
    mock_tags = [{"name": "Tag1"}, {"name": "Tag2"}, {"name": "Tag3"}]
    db_instance.get_available_tags = AsyncMock(return_value=mock_tags)

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/tags")

    expected_tags = [{"text": tag["name"], "icon": "tag"} for tag in mock_tags]
    assert response.status_code == 200
    assert response.json() == {"tags": expected_tags}
