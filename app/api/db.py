from fastapi import APIRouter, HTTPException

from app.setup_rollbar import rollbar_handler
from app.utils.db import db_instance

router = APIRouter()


@router.post("/reset_db")
@rollbar_handler
async def reset_db():
    if not db_instance.is_test_env:
        raise HTTPException(status_code=403, detail="This operation is not allowed in the current environment")

    db_instance.setup_test_db()
    return {"detail": "Database has been reset"}
