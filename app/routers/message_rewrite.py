from fastapi import APIRouter
from app.schemas.message_rewrite import MessageRewriteIn, MessageRewriteOut
from app.services.message_rewrite_service import rewrite_message

router = APIRouter(prefix="/messages", tags=["Message Rewrite"])


@router.post("/rewrite", response_model=MessageRewriteOut)
async def rewrite(payload: MessageRewriteIn):
    """Rewrite a message with key improvements and suggestions"""
    result = await rewrite_message(
        message=payload.message,
        context=payload.context
    )
    return result
