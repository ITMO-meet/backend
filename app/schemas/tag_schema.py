from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class TagSchema(BaseModel):
    name: str
    is_special: int
    description: str