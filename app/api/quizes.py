from fastapi import APIRouter, HTTPException
from app.utils.db import db_instance
from app.models.quiz import StartTestRequest
from app.setup_rollbar import rollbar_handler

router = APIRouter()


@router.get("/{test_id}")
@rollbar_handler
async def get_test_info(test_id: str):
    test = await db_instance.get_test(test_id)

    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    return {
        "name": test["name"],
        "description": test["description"],
        "questions_count": len(test["question_ids"]),
    }


@router.post("/{test_id}/start")
@rollbar_handler
async def start_test(test_id: str, payload: StartTestRequest):
    test = await db_instance.get_test(test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    result_id = await db_instance.create_result(payload.user_id, test_id, len(test["question_ids"]))

    if not result_id:
        raise HTTPException(status_code=500, detail="Error creating test results")
    return {"result_id": result_id}


@router.get("/{test_id}/question/{question_number}")
@rollbar_handler
async def get_question(test_id: str, question_number: int):
    test = await db_instance.get_test(test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    question_ids = test.get("question_ids", [])
    if question_number >= len(question_ids):
        raise HTTPException(status_code=404, detail="Question not found")

    question_id = question_ids[question_number]
    question = await db_instance.get_question_by_id(question_id)

    return {
        "description": question["description"],
        "question_number": question_number,
    }
