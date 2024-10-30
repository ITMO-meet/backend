from pydantic import BaseModel, Field
from bson import ObjectId
from typing import List, Optional, Dict, Any
from .pyObject import PyObjectId


class UserModel(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    isu: int
    username: str
    bio: Optional[str] = None
    photos: Dict[str, Any] = {}
    tags: Dict[str, List[Any]] = []
    person_params: Dict[str, Any] = {}

    class Config:
        allow_population_by_field = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
