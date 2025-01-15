from typing import Optional

from pydantic import BaseModel


class ProfileDetailsModel(BaseModel):
    isu: int
    bio: Optional[str] = ""
    weight: Optional[float] = None
    height: Optional[float] = None
    hair_color: Optional[str] = None
    zodiac_sign: Optional[str] = None
