from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from bson import ObjectId

from app.utils.db import Database


@pytest.fixture
def db_instance():
    db = Database()
    db.db = MagicMock()
    return db


def test_db_connection(db_instance):
    assert db_instance.client is not None, "DB client is not initialized"


def test_get_collection(db_instance):
    collection_name = "test_collection"

    mock_collection = MagicMock()
    mock_collection.name = collection_name
    db_instance.db.__getitem__.return_value = mock_collection

    collection = db_instance.get_collection(collection_name)

    assert collection.name == collection_name, "Collection name mismatch"


@pytest.mark.asyncio
async def test_get_available_tags():
    db_instance = Database()
    db_instance.db = MagicMock()

    mock_tags_collection = MagicMock()
    db_instance.db.__getitem__.return_value = mock_tags_collection

    fake_tags = [
        {"_id": ObjectId("507f1f77bcf86cd799439011"), "name": "Tag1"},
        {"_id": ObjectId("507f1f77bcf86cd799439012"), "name": "Tag2"},
        {"_id": ObjectId("507f1f77bcf86cd799439013"), "name": "Tag3"},
    ]

    mock_cursor = MagicMock()
    mock_cursor.to_list = AsyncMock(return_value=fake_tags)
    mock_tags_collection.find.return_value = mock_cursor

    tags = await db_instance.get_available_tags()

    expected_tags = [
        {"id": "507f1f77bcf86cd799439011", "name": "Tag1"},
        {"id": "507f1f77bcf86cd799439012", "name": "Tag2"},
        {"id": "507f1f77bcf86cd799439013", "name": "Tag3"},
    ]

    assert tags == expected_tags, "Tags returned do not match expected values"


@pytest.mark.asyncio
async def test_create_test(db_instance):
    mock_tests_collection = MagicMock()
    db_instance.db.__getitem__.return_value = mock_tests_collection

    mock_insert_result = MagicMock()
    mock_insert_result.inserted_id = ObjectId()
    mock_tests_collection.insert_one = AsyncMock(return_value=mock_insert_result)

    name = "Sample Test"
    description = "This is a sample test."
    question_ids = [ObjectId(), ObjectId()]

    inserted_id = await db_instance.create_test(name, description, question_ids)

    mock_tests_collection.insert_one.assert_awaited_once_with(
        {
            "name": name,
            "description": description,
            "question_ids": question_ids,
        }
    )

    assert inserted_id == str(mock_insert_result.inserted_id), "Inserted ID mismatch"


@pytest.mark.asyncio
async def test_get_test(db_instance):
    mock_tests_collection = MagicMock()
    db_instance.db.__getitem__.return_value = mock_tests_collection

    test_id = str(ObjectId())
    mock_test_document = {
        "_id": ObjectId(test_id),
        "name": "Sample Test",
        "description": "This is a sample test.",
        "question_ids": [ObjectId(), ObjectId()],
    }

    mock_tests_collection.find_one = AsyncMock(return_value=mock_test_document)

    test = await db_instance.get_test(test_id)

    mock_tests_collection.find_one.assert_awaited_once_with({"_id": ObjectId(test_id)})

    assert test == mock_test_document, "Test document mismatch"


@pytest.mark.asyncio
async def test_create_question(db_instance):
    mock_questions_collection = MagicMock()
    db_instance.db.__getitem__.return_value = mock_questions_collection

    mock_insert_result = MagicMock()
    mock_insert_result.inserted_id = ObjectId()
    mock_questions_collection.insert_one = AsyncMock(return_value=mock_insert_result)

    description = "What is the capital of France?"

    inserted_id = await db_instance.create_question(description)

    mock_questions_collection.insert_one.assert_awaited_once_with({"description": description})

    assert inserted_id == str(mock_insert_result.inserted_id), "Inserted ID mismatch"


@pytest.mark.asyncio
async def test_get_question_by_id(db_instance):
    mock_questions_collection = MagicMock()
    db_instance.db.__getitem__.return_value = mock_questions_collection

    question_id = str(ObjectId())
    mock_question_document = {
        "_id": ObjectId(question_id),
        "description": "What is the capital of France?",
    }

    mock_questions_collection.find_one = AsyncMock(return_value=mock_question_document)

    question = await db_instance.get_question_by_id(question_id)

    mock_questions_collection.find_one.assert_awaited_once_with({"_id": ObjectId(question_id)})

    assert question == mock_question_document, "Question document mismatch"


@pytest.mark.asyncio
async def test_create_result(db_instance):
    mock_results_collection = MagicMock()
    db_instance.db.__getitem__.return_value = mock_results_collection

    mock_insert_result = MagicMock()
    mock_insert_result.inserted_id = ObjectId()
    mock_results_collection.insert_one = AsyncMock(return_value=mock_insert_result)

    user_id = 42
    test_id = str(ObjectId())
    questions_count = 5

    inserted_id = await db_instance.create_result(user_id, test_id, questions_count)

    expected_result_data = {
        "user_id": user_id,
        "test_id": ObjectId(test_id),
        "answers": [-1] * questions_count,
        "score": None,
        "completed": False,
    }

    mock_results_collection.insert_one.assert_awaited_once_with(expected_result_data)

    assert inserted_id == str(mock_insert_result.inserted_id), "Inserted ID mismatch"


@pytest.mark.asyncio
async def test_update_result_success(db_instance):
    mock_results_collection = MagicMock()
    db_instance.db.__getitem__.return_value = mock_results_collection

    result_id = str(ObjectId())
    existing_result = {
        "_id": ObjectId(result_id),
        "answers": [-1, -1, -1],
        "completed": False,
    }
    mock_results_collection.find_one = AsyncMock(return_value=existing_result)
    mock_results_collection.update_one = AsyncMock()

    question_index = 1
    answer = 2

    updated_answers = [-1, answer, -1]

    returned_answers = await db_instance.update_result(result_id, question_index, answer)

    mock_results_collection.find_one.assert_awaited_once_with({"_id": ObjectId(result_id)})
    mock_results_collection.update_one.assert_awaited_once_with(
        {"_id": ObjectId(result_id)}, {"$set": {"answers": updated_answers}}
    )

    assert returned_answers == updated_answers, "Answers not updated correctly"


@pytest.mark.asyncio
async def test_update_result_completed(db_instance):
    mock_results_collection = MagicMock()
    db_instance.db.__getitem__.return_value = mock_results_collection

    result_id = str(ObjectId())
    existing_result = {
        "_id": ObjectId(result_id),
        "answers": [-1, -1, -1],
        "completed": True,
    }
    mock_results_collection.find_one = AsyncMock(return_value=existing_result)

    question_index = 1
    answer = 2

    returned_answers = await db_instance.update_result(result_id, question_index, answer)

    mock_results_collection.find_one.assert_awaited_once_with({"_id": ObjectId(result_id)})

    assert returned_answers is None, "Expected None when test is already completed"


@pytest.mark.asyncio
async def test_update_result_invalid_index(db_instance):
    mock_results_collection = MagicMock()
    db_instance.db.__getitem__.return_value = mock_results_collection

    result_id = str(ObjectId())
    existing_result = {
        "_id": ObjectId(result_id),
        "answers": [-1, -1, -1],
        "completed": False,
    }
    mock_results_collection.find_one = AsyncMock(return_value=existing_result)

    question_index = 5
    answer = 2

    returned_answers = await db_instance.update_result(result_id, question_index, answer)

    mock_results_collection.find_one.assert_awaited_once_with({"_id": ObjectId(result_id)})

    assert returned_answers is None, "Expected None when question index is invalid"


@pytest.mark.asyncio
async def test_get_answers(db_instance):
    mock_results_collection = MagicMock()
    db_instance.db.__getitem__.return_value = mock_results_collection

    result_id = str(ObjectId())
    mock_result = {
        "_id": ObjectId(result_id),
        "answers": [1, 2, -1],
    }

    mock_results_collection.find_one = AsyncMock(return_value=mock_result)

    answers = await db_instance.get_answers(result_id)

    mock_results_collection.find_one.assert_awaited_once_with({"_id": ObjectId(result_id)})

    assert answers == mock_result["answers"], "Answers mismatch"


@pytest.mark.asyncio
async def test_get_status(db_instance):
    mock_results_collection = MagicMock()
    db_instance.db.__getitem__.return_value = mock_results_collection

    result_id = str(ObjectId())
    mock_result = {
        "_id": ObjectId(result_id),
        "completed": True,
    }

    mock_results_collection.find_one = AsyncMock(return_value=mock_result)

    status = await db_instance.get_status(result_id)

    mock_results_collection.find_one.assert_awaited_once_with({"_id": ObjectId(result_id)})

    assert status == mock_result["completed"], "Status mismatch"


@pytest.mark.asyncio
async def test_complete_test(db_instance):
    mock_results_collection = MagicMock()
    db_instance.db.__getitem__.return_value = mock_results_collection

    result_id = str(ObjectId())
    mock_result = {
        "_id": ObjectId(result_id),
        "answers": [5, 4, 3],
        "completed": False,
    }

    expected_score = sum(mock_result["answers"]) / (len(mock_result["answers"]) * 6) * 100

    mock_results_collection.find_one = AsyncMock(return_value=mock_result)
    mock_results_collection.update_one = AsyncMock()

    score = await db_instance.complete_test(result_id)

    mock_results_collection.find_one.assert_awaited_once_with({"_id": ObjectId(result_id)})
    mock_results_collection.update_one.assert_awaited_once_with(
        {"_id": ObjectId(result_id)},
        {"$set": {"score": expected_score, "completed": True}},
    )

    assert score == expected_score, "Score calculation mismatch"


@pytest.mark.asyncio
async def test_get_result(db_instance):
    mock_results_collection = MagicMock()
    db_instance.db.__getitem__.return_value = mock_results_collection

    result_id = str(ObjectId())
    mock_result = {
        "_id": ObjectId(result_id),
        "user_id": 42,
        "test_id": ObjectId(),
        "answers": [1, 2, 3],
        "score": 50.0,
        "completed": True,
    }

    mock_results_collection.find_one = AsyncMock(return_value=mock_result)

    result = await db_instance.get_result(result_id)

    mock_results_collection.find_one.assert_awaited_once_with({"_id": ObjectId(result_id)})

    assert result == mock_result, "Result data mismatch"


@pytest.fixture
def db_instance_for_minio():
    db = Database()
    db.minio_instance = MagicMock()
    db.minio_calendar_instance = MagicMock()
    return db


def test_upload_file_to_minio(db_instance_for_minio):
    data = b"something"
    filename = "test.txt"
    content_type = "text/plain"

    result = db_instance_for_minio.upload_file_to_minio(data, filename, content_type)

    db_instance_for_minio.minio_instance.put_object.assert_called_once_with(
        db_instance_for_minio.minio_bucket_name,
        filename,
        data,
        length=-1,
        part_size=10 * 1024 * 1024,
        content_type=content_type,
    )

    assert result == f"{db_instance_for_minio.minio_bucket_name}/{filename}"


def test_uplod_json_to_minio(db_instance_for_minio):
    data = {"key": "value"}
    filename = "test.json"

    result = db_instance_for_minio.uplod_json_to_minio(data, filename)

    args, kwargs = db_instance_for_minio.minio_calendar_instance.put_object.call_args
    assert args[0] == db_instance_for_minio.minio_calendar_bucket_name
    assert args[1] == filename
    assert kwargs["content_type"] == "application/json"

    assert result == f"{db_instance_for_minio.minio_calendar_bucket_name}/{filename}"


def test_get_json_from_minio_success(db_instance_for_minio):
    filename = "schedule_123.json"
    mock_json_data = {"a": "b"}

    mock_response = MagicMock()
    mock_response.read = MagicMock()

    def mock_json_load(stream):
        return mock_json_data

    db_instance_for_minio.minio_calendar_instance.get_object.return_value = mock_response

    with patch("json.load", side_effect=mock_json_load):
        result = db_instance_for_minio.get_json_from_minio(filename)

    db_instance_for_minio.minio_calendar_instance.get_object.assert_called_once_with(
        db_instance_for_minio.minio_calendar_bucket_name,
        filename,
    )
    mock_response.close.assert_called_once()
    mock_response.release_conn.assert_called_once()

    assert result == mock_json_data


def test_get_json_from_minio_failure(db_instance_for_minio):
    filename = "no.json"

    db_instance_for_minio.minio_calendar_instance.get_object.side_effect = Exception("File not found")

    with pytest.raises(ValueError) as exc_info:
        db_instance_for_minio.get_json_from_minio(filename)

    assert "Failed to get json calendar from minio: File not found" in str(exc_info.value)


def test_delete_json_from_minio_success(db_instance_for_minio):
    filename = "test.json"

    db_instance_for_minio.delete_json_from_minio(filename)

    db_instance_for_minio.minio_calendar_instance.remove_object.assert_called_once_with(
        db_instance_for_minio.minio_calendar_bucket_name,
        filename,
    )


def test_delete_json_from_minio_failure(db_instance_for_minio):
    filename = "no.json"

    db_instance_for_minio.minio_calendar_instance.remove_object.side_effect = Exception("Remove error")

    with pytest.raises(ValueError) as exc_info:
        db_instance_for_minio.delete_json_from_minio(filename)

    assert "Failed to remove calendar data from minio: Remove error" in str(exc_info.value)
