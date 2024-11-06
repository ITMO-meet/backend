from fastapi import APIRouter, HTTPException
from app.utils.db import db_instance
from bson import ObjectId

router = APIRouter()


@router.get("/tests/{test_id}")
async def get_test_info(test_id: str):
    test = await db_instance.get_test(test_id)

    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    return{
        "name": test["name"]
        
    }