from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class UserSchema(BaseModel):
    username: str
    bio: Optional[str] = None
    photos: Dict[str, Any]
    tags: Dict[str, List[Any]]
    person_params: Dict[str, Any]
