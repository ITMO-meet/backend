import pytest
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException
from app.api.quizes_results import answer_question, complete_test, get_current_answers
from app.models.quiz import AnswerRequest


@pytest.mark.asyncio
async def test_answer_question_success():
    result_id = "result123"
    payload = AnswerRequest(question_index=1, answer="5")
    updated_answers = ["5", None, None]

    with patch(
        "app.utils.db.db_instance.update_result", new_callable=AsyncMock
    ) as mock_update_result:
        mock_update_result.return_value = updated_answers

        response = await answer_question(result_id, payload)

        assert response == {"updated_answers": updated_answers}
        mock_update_result.assert_awaited_once_with(
            result_id, payload.question_index, payload.answer
        )


@pytest.mark.asyncio
async def test_answer_question_result_not_found():
    result_id = "result123"
    payload = AnswerRequest(question_index=1, answer="5")

    with patch(
        "app.utils.db.db_instance.update_result", new_callable=AsyncMock
    ) as mock_update_result:
        mock_update_result.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await answer_question(result_id, payload)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Result not found, test not finished"
        mock_update_result.assert_awaited_once_with(
            result_id, payload.question_index, payload.answer
        )


@pytest.mark.asyncio
async def test_complete_test_success():
    result_id = "result123"
    score = 85

    with patch(
        "app.utils.db.db_instance.complete_test", new_callable=AsyncMock
    ) as mock_complete_test:
        mock_complete_test.return_value = score

        response = await complete_test(result_id)

        assert response == {"score": score}
        mock_complete_test.assert_awaited_once_with(result_id)


@pytest.mark.asyncio
async def test_complete_test_result_not_found():
    result_id = "result123"

    with patch(
        "app.utils.db.db_instance.complete_test", new_callable=AsyncMock
    ) as mock_complete_test:
        mock_complete_test.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await complete_test(result_id)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Result not found"
        mock_complete_test.assert_awaited_once_with(result_id)


@pytest.mark.asyncio
async def test_get_current_answers_success():
    result_id = "result123"
    answers = ["5", "6", None]
    status = "in_progress"

    with patch(
        "app.utils.db.db_instance.get_answers", new_callable=AsyncMock
    ) as mock_get_answers:
        mock_get_answers.return_value = answers
        with patch(
            "app.utils.db.db_instance.get_status", new_callable=AsyncMock
        ) as mock_get_status:
            mock_get_status.return_value = status

            response = await get_current_answers(result_id)

            assert response == {"answers": answers, "status": status}
            mock_get_answers.assert_awaited_once_with(result_id)
            mock_get_status.assert_awaited_once_with(result_id)
