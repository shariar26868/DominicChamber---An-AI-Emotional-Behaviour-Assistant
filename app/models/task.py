from beanie import Document, PydanticObjectId
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum


class TaskSource(str, Enum):
    user = "user"           # user manually added
    recommended = "recommended"  # added from AI recommended actions


class Task(Document):
    profile_id: PydanticObjectId
    user_id: PydanticObjectId
    title: str
    is_completed: bool = False
    source: TaskSource = TaskSource.user
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

    class Settings:
        name = "tasks"
