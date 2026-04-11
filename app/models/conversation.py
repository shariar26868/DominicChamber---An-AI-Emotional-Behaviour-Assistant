from beanie import Document, PydanticObjectId
from pydantic import BaseModel
from datetime import datetime
from typing import List

class Message(BaseModel):
    role: str
    content: str
    timestamp: datetime = datetime.utcnow()

class Conversation(Document):
    profile_id: PydanticObjectId
    user_id: PydanticObjectId
    messages: List[Message] = []
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

    class Settings:
        name = "conversations"