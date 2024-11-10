from pydantic import BaseModel
import datetime

class CreateChat(BaseModel):
    isu_1: int
    isu_2: int

class SendMessage(BaseModel):
    chat_id: str
    sender_id: int
    receiver_id: int
    text: str

class Message(BaseModel):
    message_id: str
    sender_id: int
    receiver_id: int
    text: str
    timestamp: datetime.datetime
