from pydantic import BaseModel
from typing import List
from datetime import datetime

class MessageIn(BaseModel):
    content: str

class MessageOut(BaseModel):
    role: str
    content: str
    timestamp: datetime

class ConversationOut(BaseModel):
    id: str
    profile_id: str
    messages: List[MessageOut]
    created_at: datetime
    updated_at: datetime