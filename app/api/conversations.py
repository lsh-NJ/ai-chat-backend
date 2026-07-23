from fastapi import APIRouter, HTTPException
from app.models.conversation import Conversation
from app.services import conversation_services

from app.db.database import (
    get_conversation,
    list_messages,
)
from app.schemas.conversation import (
    ConversationCreateRequest,
    ConversationResponse,
    MessageResponse,
)

router = APIRouter(tags=["conversation"])


# 创建会话
@router.post("/conversations", response_model=ConversationResponse)
def create_conversation_api(request: ConversationCreateRequest):
    conversation_id = conversation_services.create_conversation(title=request.title)
    conversation = conversation_services.get_conversation(conversation_id)
    return ConversationResponse(
        id=conversation.id,
        title=conversation.title,
        create_at=conversation.create_at,
    )


# 查看会话列表
@router.get("/conversations", response_model=list[ConversationResponse])
def list_conversations_api():
    conversations = conversation_services.list_conversation()
    return [
        ConversationResponse(
            id=conversation.id,
            title=conversation.title,
            create_at=conversation.create_at,
        )
        for conversation in conversations
    ]


# 查看某个会话的历史记录
@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=list[MessageResponse],
)
def list_messages_api(conversation_id: int):
    conversation = get_conversation(conversation_id)

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="conversation_id not found",
        )

    messages = list_messages(conversation_id)

    return [
        MessageResponse(
            id=row["id"],
            conversation_id=row["conversation_id"],
            role=row["role"],
            content=row["content"],
            created_at=row["created_at"],
        )
        for row in messages
    ]