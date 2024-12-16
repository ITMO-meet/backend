import pytest
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException
from app.api.quizes import get_test_info, start_test, get_question
from app.models.quiz import StartTestRequest


@pytest.mark.asyncio
async def test_get_test_info_success():
    test_id = "test123"
    test_data = {
        "name": "Test",
        "description": "Description",
        "question_ids": ["q1", "q2", "q3"],
    }

    with patch("app.utils.db.db_instance.get_test", new_callable=AsyncMock) as mock_get_test:
        mock_get_test.return_value = test_data

        response = await get_test_info(test_id)

        assert response == {
            "name": test_data["name"],
            "description": test_data["description"],
            "questions_count": len(test_data["question_ids"]),
        }


@pytest.mark.asyncio
async def test_get_test_info_not_found():
    test_id = "test123"

    with patch("app.utils.db.db_instance.get_test", new_callable=AsyncMock) as mock_get_test:
        mock_get_test.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await get_test_info(test_id)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Test not found"


@pytest.mark.asyncio
async def test_start_test_success():
    test_id = "test123"
    payload = StartTestRequest(user_id="456")
    test_data = {
        "question_ids": ["q1", "q2", "q3"],
    }
    result_id = "result789"

    with patch("app.utils.db.db_instance.get_test", new_callable=AsyncMock) as mock_get_test:
        mock_get_test.return_value = test_data
        with patch("app.utils.db.db_instance.create_result", new_callable=AsyncMock) as mock_create_result:
            mock_create_result.return_value = result_id

            response = await start_test(test_id, payload)

            assert response == {"result_id": result_id}


@pytest.mark.asyncio
async def test_start_test_test_not_found():
    test_id = "test123"
    payload = StartTestRequest(user_id="456")

    with patch("app.utils.db.db_instance.get_test", new_callable=AsyncMock) as mock_get_test:
        mock_get_test.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await start_test(test_id, payload)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Test not found"


@pytest.mark.asyncio
async def test_start_test_create_result_failure():
    test_id = "test123"
    payload = StartTestRequest(user_id="456")
    test_data = {
        "question_ids": ["q1", "q2", "q3"],
    }

    with patch("app.utils.db.db_instance.get_test", new_callable=AsyncMock) as mock_get_test:
        mock_get_test.return_value = test_data
        with patch("app.utils.db.db_instance.create_result", new_callable=AsyncMock) as mock_create_result:
            mock_create_result.return_value = None

            with pytest.raises(HTTPException) as exc_info:
                await start_test(test_id, payload)

            assert exc_info.value.status_code == 500
            assert exc_info.value.detail == "Error creating test results"


@pytest.mark.asyncio
async def test_get_question_success():
    test_id = "test123"
    question_number = 1
    test_data = {
        "question_ids": ["q1", "q2", "q3"],
    }
    question_data = {
        "description": "What is 2 + 2?",
    }

    with patch("app.utils.db.db_instance.get_test", new_callable=AsyncMock) as mock_get_test:
        mock_get_test.return_value = test_data
        with patch("app.utils.db.db_instance.get_question_by_id", new_callable=AsyncMock) as mock_get_question_by_id:
            mock_get_question_by_id.return_value = question_data

            response = await get_question(test_id, question_number)

            assert response == {
                "description": question_data["description"],
                "question_number": question_number,
            }


@pytest.mark.asyncio
async def test_get_question_test_not_found():
    test_id = "test123"
    question_number = 1

    with patch("app.utils.db.db_instance.get_test", new_callable=AsyncMock) as mock_get_test:
        mock_get_test.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await get_question(test_id, question_number)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Test not found"


@pytest.mark.asyncio
async def test_get_question_question_not_found():
    test_id = "test123"
    question_number = 5
    test_data = {
        "question_ids": ["q1", "q2", "q3"],
    }

    with patch("app.utils.db.db_instance.get_test", new_callable=AsyncMock) as mock_get_test:
        mock_get_test.return_value = test_data

        with pytest.raises(HTTPException) as exc_info:
            await get_question(test_id, question_number)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Question not found"
