from fastapi import APIRouter, HTTPException
from collections.abc import Iterator
from fastapi.responses import StreamingResponse
from app.services.llm_service import (
    LLMStreamError,
    call_llm,
    stream_llm,
)
from app.db.database import (
    create_conversation,
    get_conversation,
    list_recent_messages_for_llm,
    save_message,
)
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
)

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    conversation_id = request.conversation_id

    if conversation_id is None:
        conversation_id = create_conversation(
            title=request.message[:30]
        )
    elif get_conversation(conversation_id) is None:
        raise HTTPException(
            status_code=404,
            detail="conversation_id not found",
        )

    save_message(
        conversation_id=conversation_id,
        role="user",
        content=request.message,
    )

    history_messages = list_recent_messages_for_llm(
        conversation_id=conversation_id,
        limit=20,
    )

    reply = call_llm(history_messages)

    save_message(
        conversation_id=conversation_id,
        role="assistant",
        content=reply,
    )

    return ChatResponse(
        reply=reply,
        conversation_id=conversation_id,
    )


# 流式对话接口
@router.post("/chat/stream")
def chat_stream(request: ChatRequest):
    conversation_id = request.conversation_id

    if conversation_id is None:
        conversation_id = create_conversation(
            title=request.message[:30]
        )

    elif get_conversation(conversation_id) is None:
        raise HTTPException(
            status_code=404,
            detail="conversation_id not found",
        )

    save_message(
        conversation_id=conversation_id,
        role="user",
        content=request.message,
    )

    history_messages = list_recent_messages_for_llm(
        conversation_id=conversation_id,
        limit=20,
    )

    llm_chunks = stream_llm(history_messages)

    def generate_response() -> Iterator[str]:
        reply_parts: list[str] = []

        try:
            for chunk in llm_chunks:
                reply_parts.append(chunk)
                yield chunk

        except LLMStreamError as e:
            yield f"\n\n[流式响应中断：{e}]\n"

        finally:
            full_reply = "".join(reply_parts).strip()

            if full_reply:
                save_message(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=full_reply,
                )

    return StreamingResponse(
        generate_response(),
        media_type="text/plain; charset=utf-8",
        headers={
            "X-Conversation-Id": str(conversation_id),
            "Cache-Control": "no-cache",
        },
    )
