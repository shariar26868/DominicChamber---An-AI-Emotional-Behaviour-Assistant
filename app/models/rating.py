from beanie import Document, PydanticObjectId
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Rating(Document):
    profile_id: PydanticObjectId
    user_id: PydanticObjectId
    score: int                      # 1-10
    note: Optional[str] = None
    created_at: datetime = datetime.utcnow()

    class Settings:
        name = "ratings"