import pytest
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
