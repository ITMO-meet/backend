from typing import Optional

from pydantic import BaseModel


class CreateChat(BaseModel):
    isu_1: int
    isu_2: int


class SendMessage(BaseModel):
    chat_id: str
    sender_id: int
    receiver_id: int
    media_id: Optional[str] = ""
    text: Optional[str] = ""
