from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class UserModel(BaseModel):
    isu: int
    username: str
    bio: Optional[str] = None
    photos: Dict[str, Any] = {}
    tags: Dict[str, List[Any]] = []
    person_params: Dict[str, Any] = {}

    class Config:
        allow_population_by_field = True
        arbitrary_types_allowed = True
