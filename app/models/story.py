from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class GetStory(BaseModel):
    isu_from: int
    isu_whose: int