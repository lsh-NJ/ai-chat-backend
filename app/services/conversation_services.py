from app.models.conversation import Conversation
from app.repositories import conversation_repository

def create_conversation(title: str | None) -> Conversation:
    conversation_id = conversation_repository.create(title=title)
    conversation = conversation_repository.get_by_id(conversation_id=conversation_id)

    if conversation is None:
        raise RuntimeError(
            "conversation was not found after creation"
        )

    return conversation

def get_conversation(id: int) -> Conversation:
    return conversation_repository.get_by_id(id)

def list_conversation() -> list[Conversation]:
    return conversation_repository.list_all()
