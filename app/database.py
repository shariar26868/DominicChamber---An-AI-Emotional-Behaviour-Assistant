from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.config import settings
from app.models.user import User
from app.models.person_profile import PersonProfile
from app.models.conversation import Conversation
from app.models.rating import Rating

async def init_db():
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.db_name]
    await init_beanie(
        database=db,
        document_models=[User, PersonProfile, Conversation, Rating]
    )