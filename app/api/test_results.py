from fastapi import APIRouter, HTTPException
from app.utils.db import db_instance
from app.models.test import AnswerRequest

router = APIRouter()


@router.post("/answer/{result_id}")
async def answer_question(result_id: str, payload: AnswerRequest):
    updated_answer = await db_instance.update_result(result_id, payload.answer)

    if updated_answer is None:
        raise HTTPException(
            status_code=404, detail="Result not found, test not finished"
        )

    return {"updated_answers": updated_answer}


@router.post("/complete/{result_id}")
async def complete_test(result_id: str):
    score = await db_instance.complete_test(result_id)

    if score is None:
        raise HTTPException(status_code=404, detail="Result not found")
    return {"score": score}
