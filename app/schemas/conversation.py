from pydantic import BaseModel, Field

# 创建会话时的请求体
class ConversationCreateRequest(BaseModel):
    title: str | None = Field(default=None, max_length=100)

# 返回会话信息
class ConversationResponse(BaseModel):
    id: int
    title: str | None
    created_at: str

# 返回消息信息
class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    created_at: str