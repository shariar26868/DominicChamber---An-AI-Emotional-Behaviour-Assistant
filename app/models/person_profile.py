from beanie import Document, PydanticObjectId
from pydantic import Field, BaseModel
from datetime import datetime
from typing import Optional, List

class QuestionAnswer(BaseModel):
    question: str
    selected_option: str

class PersonProfile(Document):
    user_id: PydanticObjectId
    name: str
    relationship: str
    description: str
    personality_traits: List[str] = []
    questionnaire_answers: List[QuestionAnswer] = []
    profile_finalized: bool = False
    created_at: datetime = datetime.utcnow()

    class Settings:
        name = "person_profiles"