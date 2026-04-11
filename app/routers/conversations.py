from fastapi import APIRouter, HTTPException
from app.schemas.conversation import MessageIn, MessageOut, ConversationOut
from app.schemas.recent_interactions import RecentInteractionsOut, RecentInteraction
from app.models.conversation import Conversation, Message
from app.models.person_profile import PersonProfile
from app.services.conversation_service import get_ai_reply
from app.utils.exceptions import InvalidObjectIdException
from beanie import PydanticObjectId
from bson.errors import InvalidId
from datetime import datetime
from typing import List

router = APIRouter(prefix="/profiles", tags=["Conversations"])


@router.post("/{profile_id}/chat")
async def chat(profile_id: str, user_id: str, payload: MessageIn):
    try:
        profile = await PersonProfile.get(PydanticObjectId(profile_id))
    except InvalidId:
        raise InvalidObjectIdException(profile_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # existing conversation খোঁজো, না থাকলে নতুন বানাও
    try:
        conversation = await Conversation.find_one(
            Conversation.profile_id == PydanticObjectId(profile_id),
            Conversation.user_id == PydanticObjectId(user_id)
        )
    except InvalidId:
        raise InvalidObjectIdException(user_id if not conversation else profile_id)

    if not conversation:
        try:
            conversation = Conversation(
                profile_id=PydanticObjectId(profile_id),
                user_id=PydanticObjectId(user_id),
                messages=[]
            )
        except InvalidId as e:
            raise InvalidObjectIdException(user_id)
        await conversation.insert()

    # user message add করো
    user_message = Message(role="user", content=payload.content)
    conversation.messages.append(user_message)

    # AI reply নাও
    ai_reply_text = await get_ai_reply(
        profile=profile,
        messages=conversation.messages
    )

    # assistant message add করো
    assistant_message = Message(role="assistant", content=ai_reply_text)
    conversation.messages.append(assistant_message)
    conversation.updated_at = datetime.utcnow()

    await conversation.save()

    return {
        "user_message": payload.content,
        "ai_reply": ai_reply_text,
        "conversation_id": str(conversation.id)
    }


@router.get("/{profile_id}/conversations", response_model=List[ConversationOut])
async def get_conversations(profile_id: str):
    try:
        conversations = await Conversation.find(
            Conversation.profile_id == PydanticObjectId(profile_id)
        ).to_list()
    except InvalidId:
        raise InvalidObjectIdException(profile_id)

    return [
        ConversationOut(
            id=str(c.id),
            profile_id=str(c.profile_id),
            messages=[
                MessageOut(
                    role=m.role,
                    content=m.content,
                    timestamp=m.timestamp
                ) for m in c.messages
            ],
            created_at=c.created_at,
            updated_at=c.updated_at
        )
        for c in conversations
    ]


@router.get("/user/{user_id}/recent", response_model=RecentInteractionsOut)
async def get_recent_interactions(user_id: str):
    """Get recent conversations for a user sorted by latest activity"""
    try:
        # Find all conversations for this user, sorted by updated_at descending
        conversations = await Conversation.find(
            Conversation.user_id == PydanticObjectId(user_id)
        ).sort([("updated_at", -1)]).limit(20).to_list()
    except InvalidId:
        raise InvalidObjectIdException(user_id)

    interactions = []
    for conv in conversations:
        try:
            profile = await PersonProfile.get(conv.profile_id)
            if profile and conv.messages:
                # Get the last message
                last_message = conv.messages[-1].content
                last_message_time = conv.messages[-1].timestamp
                
                interaction = RecentInteraction(
                    conversation_id=str(conv.id),
                    profile_id=str(profile.id),
                    person_name=profile.name,
                    relationship=profile.relationship,
                    last_message=last_message[:100],  # First 100 chars
                    last_message_time=last_message_time,
                    message_count=len(conv.messages)
                )
                interactions.append(interaction)
        except Exception:
            continue

    return RecentInteractionsOut(
        interactions=interactions,
        total=len(interactions)
    )