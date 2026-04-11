from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class RatingCreate(BaseModel):
    score: int = Field(..., ge=1, le=10)
    note: Optional[str] = None

class RatingOut(BaseModel):
    id: str
    profile_id: str
    score: int
    note: Optional[str]
    created_at: datetime

class AverageRating(BaseModel):
    profile_id: str
    person_name: str
    average_score: float
    total_ratings: int