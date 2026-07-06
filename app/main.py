from fastapi import FastAPI

# 创建 app 对象，后面是后端应用本体
app = FastAPI(
    title="AI Chat Backend",
    description="一个由 FastAPI 实现的简单 AI 后端",
    version="0.1.0",
)

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