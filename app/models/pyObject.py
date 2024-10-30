from pydantic import BaseModel, Field
from bson import ObjectId
from typing import List, Optional, Dict, Any


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError(f"Invalid ObjectId: {ObjectId(v)}")
        return ObjectId(v)
