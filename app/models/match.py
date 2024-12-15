from pydantic import BaseModel

class UserAction(BaseModel):
    user_id: int
    target_id: int