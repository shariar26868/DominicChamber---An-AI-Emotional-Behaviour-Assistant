from beanie import Document, PydanticObjectId
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Rating(Document):
    profile_id: PydanticObjectId
    user_id: PydanticObjectId
    question_number: Optional[int] = None  # which AI-generated question this rating is for
    score: int                              # 1-10
    note: Optional[str] = None
    created_at: datetime = datetime.utcnow()

    class Settings:
        name = "ratings"