from pydantic import BaseModel
from typing import List

class KeyPoints(BaseModel):
    points: List[str]

class ExpectedOutcome(BaseModel):
    description: str

class GuidanceOut(BaseModel):
    profile_id: str
    person_name: str
    personality_traits: List[str]
    summary: str
    key_points: List[str]
    expected_outcome: str

class TraitsOut(BaseModel):
    profile_id: str
    person_name: str
    personality_traits: List[str]