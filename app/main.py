from fastapi import FastAPI, HTTPException

from app.core.config import settings
from app.services.external_api import fetch_github_status
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm_service import call_llm
from app.db.database import (
    create_conversation,
    get_conversation,
    init_db,
    save_message,
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

    reply = call_llm(request.message)

    save_message(
        conversation_id=conversation_id,
        role="assistant",
        content=reply,
    )

    return ChatResponse(
        reply=reply,
        conversation_id=conversation_id,
    )