from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    email: EmailStr

class UserOut(BaseModel):
    id: str
    name: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True