from pydantic import BaseModel
from typing import List, Optional, Dict


class UserModel(BaseModel):
    isu: int
    username: Optional[str] = ""
    bio: Optional[str] = ""
    logo: Optional[str] = ""
    photos: List[str] = []
    mainFeatures: List[Dict[str, str]] = []
    interests: List[Dict[str, str]] = []
    itmo: List[Dict[str, str]] = []
    gender_preferences: List[Dict[str, str]] = []
    relationship_preferences: List[Dict[str, str]] = []
    isStudent: bool = True

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
