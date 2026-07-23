from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.core.config import settings
from app.db.database import (
    init_db,
)

from app.api.chat import router as chat_router
from app.api.system import router as system_router
from app.api.conversations import router as conversation_router

@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


# 创建 app 对象，后面是后端应用本体
app = FastAPI(
    title="AI Chat Backend",
    description="一个由 FastAPI 实现的简单 AI 后端",
    version=settings.app_version,
    lifespan=lifespan,
)

app.include_router(chat_router)
app.include_router(system_router)
app.include_router(conversation_router)

