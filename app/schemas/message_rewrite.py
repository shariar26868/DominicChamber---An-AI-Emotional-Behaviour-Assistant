from pydantic import BaseModel
from typing import List

class MessageRewriteIn(BaseModel):
    message: str
    context: str = ""  # Optional: relationship or context about the recipient

class Improvement(BaseModel):
    title: str
    description: str

class MessageRewriteOut(BaseModel):
    original_message: str
    rewritten_message: str
    key_improvements: List[Improvement]
    suggestions: List[Improvement]
