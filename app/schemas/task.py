from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class TaskSource(str, Enum):
    user = "user"
    recommended = "recommended"


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1)
    source: TaskSource = TaskSource.user


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1)
    is_completed: Optional[bool] = None


class TaskOut(BaseModel):
    id: str
    profile_id: str
    user_id: str
    title: str
    is_completed: bool
    source: TaskSource
    created_at: datetime
    updated_at: datetime


class RecommendedAction(BaseModel):
    title: str


class RecommendedActionsResponse(BaseModel):
    profile_id: str
    recommended_actions: List[RecommendedAction]


class TaskListResponse(BaseModel):
    profile_id: str
    total: int
    completed: int
    tasks: List[TaskOut]
