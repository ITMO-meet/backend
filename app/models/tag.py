from pydantic import BaseModel, Field
from bson import ObjectId
from typing import List, Optional
from .pyObject import PyObjectId


class TagModel(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    name: str
    is_special: (
        int  # 0 user tags, 1 - preference tags  # 0 user tags, 1 - preference tags
    )
    description: str

    class Config:
        allow_population_by_field = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class TagSelectionModel(BaseModel):
    isu: int
    tags: List[str]
