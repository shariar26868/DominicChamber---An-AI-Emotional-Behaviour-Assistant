from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime
from beanie import PydanticObjectId
from bson.objectid import ObjectId
from bson.errors import InvalidId

class QuestionAnswerItem(BaseModel):
    question: str
    selected_option: str

class ProfileCreate(BaseModel):
    user_id: str
    name: str
    relationship: str
    description: str
    
    @field_validator('user_id')
    @classmethod
    def validate_user_id(cls, v):
        try:
            ObjectId(v)
        except (InvalidId, TypeError):
            raise ValueError(f"'{v}' is not a valid ObjectId. Must be a 24-character hex string or 12-byte input")
        return v

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    relationship: Optional[str] = None
    description: Optional[str] = None

class ProfileOut(BaseModel):
    id: str
    user_id: str
    name: str
    relationship: str
    description: str
    personality_traits: List[str] = []
    profile_finalized: bool
    created_at: datetime

class ProfileWithTraits(ProfileOut):
    questionnaire_answers: List[QuestionAnswerItem] = []