# AI Chat Backend
## 项目介绍
一个由 FastAPI 实现的简单 AI 后端

## 已实现功能
* 会话与指定会话中进行聊天
* 支持非流式和流式输出
* 聊天上下文由该会话最多20条聊天记录构成

## 技术栈
- python
- FastAPI
- Httpx
- Uvicorn
- SqLite3

## Features
- Health check API
- Auto-generated API docs

## 运行测试
```bash
pytest
```

## 快速开始
```bash
pthon3 -m venv .venv
source -m pip install -r requirments.txt
uvicorn app.main:app --reload
```
