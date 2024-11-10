from pydantic import BaseModel


class CreateChat(BaseModel):
    isu_1: int
    isu_2: int