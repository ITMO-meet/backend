import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.utils.db import Database


@pytest.fixture
def db_instance():
    return Database()


def test_db_connection(db_instance):
    assert db_instance.client is not None, "DB client is not initialized"


def test_get_collection(db_instance):
    collection_name = "test_collection"
    collection = db_instance.get_collection(collection_name)
    assert collection.name == collection_name, "Collection name mismatch"


import pytest
from unittest.mock import AsyncMock, MagicMock
from app.utils.db import Database


@pytest.mark.asyncio
async def test_get_available_tags():
    db_instance = Database()
    db_instance.db = MagicMock()

    mock_tags_collection = MagicMock()
    db_instance.db.__getitem__.return_value = mock_tags_collection

    fake_tags = [
        {"name": "Tag1"},
        {"name": "Tag2"},
        {"name": "Tag3"},
    ]

    mock_cursor = MagicMock()
    mock_cursor.to_list = AsyncMock(return_value=fake_tags)
    mock_tags_collection.find.return_value = mock_cursor

    tags = await db_instance.get_available_tags()

    assert tags == [
        "Tag1",
        "Tag2",
        "Tag3",
    ], "Tags returned do not match expected values"
