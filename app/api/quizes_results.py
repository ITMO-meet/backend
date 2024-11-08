from fastapi import APIRouter, HTTPException
from app.utils.db import db_instance
from app.models.quiz import AnswerRequest

router = APIRouter()


@router.post("/answer/{result_id}")
async def answer_question(result_id: str, payload: AnswerRequest):
    updated_answers = await db_instance.update_result(
        result_id, payload.question_index, payload.answer
    )

    if updated_answers is None:
        raise HTTPException(
            status_code=404, detail="Result not found, test not finished"
        )

    return {"updated_answers": updated_answers}


@router.post("/complete/{result_id}")
async def complete_test(result_id: str):
    score = await db_instance.complete_test(result_id)

    if score is None:
        raise HTTPException(status_code=404, detail="Result not found")
    return {"score": score}


@router.get("/current_result/{result_id}/answers")
async def get_current_answers(result_id: str):
    answers = await db_instance.get_answers(result_id)
    status = await db_instance.get_status(result_id)
    if answers is None:
        raise HTTPException(status_code=404, detail="Result not found")
    return {"answers": answers, "status": status}
