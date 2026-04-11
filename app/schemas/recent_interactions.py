from pydantic import BaseModel
from typing import List
from datetime import datetime

class RecentInteraction(BaseModel):
    conversation_id: str
    profile_id: str
    person_name: str
    relationship: str
    last_message: str
    last_message_time: datetime
    message_count: int

class RecentInteractionsOut(BaseModel):
    interactions: List[RecentInteraction]
    total: int
