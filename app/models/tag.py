from pydantic import BaseModel, Field
from bson import ObjectId
from typing import List, Optional, Dict, Any
from .pyObject import PyObjectId


class TagModel(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    name: str
    is_special: int
    description: str

    class Config:
        allow_population_by_field = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
