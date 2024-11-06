from pydantic import BaseModel


class TagSchema(BaseModel):
    name: str
    is_special: int
    description: str