from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class UserModel(BaseModel):
    isu: int
    username: str
    bio: Optional[str] = None
    photos: Dict[str, Any] = {}
    tags: Dict[str, List[Any]] = []
    person_params: Dict[str, Any] = {}
    preferences: Dict[str, Any] = {
        "gender_preference": None,
        "relationship_preference": [] 
    }

    class Config:
        allow_population_by_field = True
        arbitrary_types_allowed = True

class UsernameSelectionModel(BaseModel):
    isu: int
    username: str

class GenderPreferencesSelectionModel(BaseModel):
    isu: int
    gender_preference: str

class RelationshipsPreferencesSelectionModel(BaseModel):
    isu: int
    relationship_preference: List[str] 