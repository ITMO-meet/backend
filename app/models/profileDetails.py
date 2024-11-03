from pydantic import BaseModel
from typing import Optional


class ProfileDetailsModel(BaseModel):
    isu: int
    bio: Optional[str] = ""
    weight: Optional[float] = None
    height: Optional[float] = None
    hair_color: Optional[str] = None
    zodiac_sign: Optional[str] = None
