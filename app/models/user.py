from beanie import Document
from pydantic import EmailStr
from datetime import datetime
from typing import Optional

class User(Document):
    name: str
    email: EmailStr
    created_at: datetime = datetime.utcnow()

    class Settings:
        name = "users"