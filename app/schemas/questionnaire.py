from pydantic import BaseModel
from typing import List

class QuestionOption(BaseModel):
    label: str
    value: str

class QuestionItem(BaseModel):
    question_id: str
    question: str
    options: List[QuestionOption]

class QuestionnaireResponse(BaseModel):
    profile_id: str
    questions: List[QuestionItem]

class AnswerItem(BaseModel):
    question_id: str
    question: str
    selected_option: str

class AnswerSubmit(BaseModel):
    profile_id: str
    answers: List[AnswerItem]