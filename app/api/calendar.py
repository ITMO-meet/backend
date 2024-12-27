from fastapi import APIRouter, HTTPException
from app.utils.db import db_instance
from app.setup_rollbar import rollbar_handler

router = APIRouter()

@router.get("/get_calendar/{isu}")
@rollbar_handler
async def update_calendar(isu: int):
    try:
        filename = f"schedule_{isu}.json"
        schedule = db_instance.get_json_from_minio(filename)
        return schedule["data"]
    except ValueError as e:
        raise HTTPException(status_code=404, detail=f"Schedule not found: {e}")