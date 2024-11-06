from pydantic import BaseModel, Field
from typing import List, Optional
from bson import ObjectId
from app.models.pyObject import PyObjectId


class TestModel(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    name: str
    description: str
    questions: List[PyObjectId]

    class Config:
        allow_population_by_field = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class QuestionModel(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    description: str

    class Config:
        allow_population_by_field = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class ResultModel(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: int
    test_id: PyObjectId
    answers: List[int] = []
    score: Optional[float] = None
    completed: bool = False

    class Config:
        allow_population_by_field = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class StartTestRequest(BaseModel):
    user_id: int


class AnswerRequest(BaseModel):
    answer: int
