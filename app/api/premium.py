from fastapi import APIRouter, HTTPException
import datetime

from app.setup_rollbar import rollbar_handler
from app.utils.db import db_instance


router = APIRouter()


@router.post("/set_premium")
@rollbar_handler
async def set_premium(isu: int):
    existing_premium = await db_instance.db["premium"].find_one(
        {"isu": isu, "validUntil": {"$gte": datetime.datetime.utcnow()}}
    )
    if existing_premium:
        raise HTTPException(status_code=400, detail="Premium is already active")

    result = await db_instance.create_premium(isu)
    return {"premium_id": result}


@router.get("/check_premium")
@rollbar_handler
async def check_premium(isu: int):
    premium = await db_instance.db["premium"].find_one(
        {"isu": isu, "validUntil": {"$gte": datetime.datetime.utcnow()}}
    )
    return {"isPremium": bool(premium)}

