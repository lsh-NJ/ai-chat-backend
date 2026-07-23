from app.models.message import Message
from app.repositories import chat_repository
from app.services import conversation_services
from app.services.llm_service import call_llm

# 保存消息：
def save_message(
    conversation_id: int,
    role: str,
    content: str
) -> int: 
    message_id = chat_repository.save_message(
        conversation_id=conversation_id,
        role=role,
        content=content,
    )
    return message_id

# 获取历史消息：
def get_history_messages(
    conversation_id: int,
    limit: int = 20,
) -> list[Message]:
    return chat_repository.list_recent_messages(
        conversation_id=conversation_id,
        limit=20,
    )


# chat
def chat(
    conversation_id: int | None,
    message: str,
) -> list[Message]:
    # 无对话 id
    if conversation_id is None:
        conversation_id = conversation_services.create_conversation(
            title=message[:30],
        )
    # 无效对话 id
    elif conversation_services.get_conversation(conversation_id) is None:
        raise RuntimeError(
            "invalid conversation ID"
        )

    save_message(
        conversation_id=conversation_id,
        role="user",
        content=message,
    )

    history_messages = get_history_messages(
        conversation_id=conversation_id,
        limit=20,
    )

    reply: str = call_llm(history_messages) 

    save_message(
        conversation_id=conversation_id,
        role="assistant",
        content=reply,
    )

    return 
