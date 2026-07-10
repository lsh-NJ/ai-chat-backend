from fastapi import FastAPI, HTTPException
from collections.abc import Iterator
from fastapi.responses import StreamingResponse

from app.core.config import settings
from app.services.external_api import fetch_github_status
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm_service import (
    LLMStreamError,
    call_llm,
    stream_llm,
)
from app.db.database import (
    create_conversation,
    get_conversation,
    init_db,
    list_conversations,
    list_messages,
    list_recent_messages_for_llm,
    save_message,
)
from app.schemas.conversation import (
    ConversationCreateRequest,
    ConversationResponse,
    MessageResponse,
)

# 创建 app 对象，后面是后端应用本体
app = FastAPI(
    title="AI Chat Backend",
    description="一个由 FastAPI 实现的简单 AI 后端",
    version=settings.app_version,
)

init_db()

# 定义首页接口，当用户get请求访问/就执行root函数
@app.get("/")
def root():
    return {
        "message": "Welcome to AI Chat Backend"
    }

# /health 是用来检查服务有没有正常运行的常用接口
@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "AI Chat Backend is runing"
    }

@app.get("/config/test")
def config_test():
    return {
        "app_name": settings.app_name,
        "app_version": settings.app_version,
        "has_test_api_key": settings.test_api_key is not None
    }

@app.get("/external_api/test")
def external_test():
    data = fetch_github_status()
    return {
        "message": "External API request success",
        "current_user_url": data.get("current_user_url"),
        "repository_url": data.get("repository_url"),
    }

@app.post("/chat/test", response_model=ChatResponse)
def chat_test(request: ChatRequest):
    return ChatResponse(
        reply=f"你刚才说的是:{request.message}"
    )

@app.post("/chat", response_model=ChatResponse)
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
@app.post("/chat/stream")
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

# 创建会话
@app.post("/conversations", response_model=ConversationResponse)
def create_conversation_api(request: ConversationCreateRequest):
    conversation_id = create_conversation(title=request.title)
    conversation = get_conversation(conversation_id)

    return ConversationResponse(
        id=conversation["id"],
        title=conversation["title"],
        created_at=conversation["created_at"],
    )

# 查看会话列表
@app.get("/conversations", response_model=list[ConversationResponse])
def list_conversations_api():
    conversations = list_conversations()

    return [
        ConversationResponse(
            id=row["id"],
            title=row["title"],
            created_at=row["created_at"],
        )
        for row in conversations
    ]

# 查看某个会话的历史记录
@app.get(
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