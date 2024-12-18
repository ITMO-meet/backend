from pydantic import BaseModel


class GetStory(BaseModel):
    isu_from: int
    isu_whose: int
    story_id: str
