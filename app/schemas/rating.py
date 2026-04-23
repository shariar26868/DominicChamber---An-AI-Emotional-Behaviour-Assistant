from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class RatingCreate(BaseModel):
    question_number: int = Field(..., ge=1, description="Which AI-generated question this rating is for")
    score: int = Field(..., ge=1, le=10)
    note: Optional[str] = None


class RatingOut(BaseModel):
    id: str
    profile_id: str
    question_number: Optional[int]
    score: int
    note: Optional[str]
    created_at: datetime


class RatingBulkResponse(BaseModel):
    profile_id: str
    ratings: List[RatingOut]


class AverageRating(BaseModel):
    profile_id: str
    person_name: str
    average_score: float
    total_ratings: int


class RatingQuestion(BaseModel):
    question_number: int
    question: str


class RatingQuestionsRequest(BaseModel):
    conversation_id: str


class RatingQuestionsResponse(BaseModel):
    profile_id: str
    conversation_id: str
    questions: List[RatingQuestion]
