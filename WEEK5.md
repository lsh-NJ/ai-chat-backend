# Week 5：把 v0.1 拆成真正的后端项目

> 执行方式：项目驱动。遇到 Python、SQL、HTTP 缺口时，只补当前任务需要的部分。  
> 本周暂不引入 PostgreSQL、Redis、JWT 和 Agent，避免一次改动过多。

## 本周目标

把当前能运行但高度集中在 `app/main.py` 的 v0.1，重构为职责清晰、可以继续扩展的 Chat Backend V1.1。

本周结束时应做到：

- `app/main.py` 只负责创建和组装 FastAPI 应用。
- Chat、Conversation、System 路由分开。
- 路由层不直接访问 SQLite，也不直接调用外部模型。
- 业务层不依赖 FastAPI 的 `HTTPException`。
- 数据访问集中在 repository 层。
- 测试不请求真实模型 API。
- 原有接口行为保持兼容。

## 现状问题清单

- [ ] `app/main.py` 重复导入 `FastAPI` 和 `HTTPException`
- [ ] 已定义 `lifespan`，但创建 `FastAPI` 时没有传入
- [ ] 路由、业务流程、数据库访问和流式响应混在一起
- [ ] 路由函数直接调用 SQLite 函数
- [ ] LLM service 抛出 Web 层的 `HTTPException`
- [ ] 同步 HTTP 和同步 SQLite 会阻塞请求线程
- [ ] 测试数量少，且缺少 LLM mock 和数据库隔离
- [ ] README 的启动命令存在拼写和命令错误

## 目标目录

```text
app/
├── api/
│   ├── chat.py
│   ├── conversations.py
│   └── system.py
├── core/
│   ├── config.py
│   └── exceptions.py
├── db/
│   └── database.py
├── repositories/
│   └── conversation_repository.py
├── schemas/
│   ├── chat.py
│   └── conversation.py
├── services/
│   ├── chat_service.py
│   └── llm_service.py
└── main.py
```

该目录是本周目标，不要求第一天一次建完。

## Day 1：拆应用入口和路由

### 任务

- [x] 删除 `app/main.py` 的重复导入
- [x] 创建 `app/api/system.py`
- [x] 把 `/` 和 `/health` 移入 system router
- [x] 创建 `app/api/conversations.py`
- [x] 把会话创建、列表和消息历史接口移入 conversation router
- [x] 创建 `app/api/chat.py`
- [x] 把 `/chat` 和 `/chat/stream` 移入 chat router
- [x] 在 `app/main.py` 注册三个 router
- [x] 将 `lifespan` 传给 `FastAPI`
- [x] 保证 URL、状态码和响应结构不变

### 只补这些基础

- Python 模块与包
- `import` 与依赖方向
- FastAPI `APIRouter`
- FastAPI lifespan
- 回归测试

### 验收

```bash
pytest
```

- [x] 现有测试全部通过
- [x] `/health` 返回与重构前一致
- [x] `app/main.py` 不包含业务处理逻辑
- [x] `app/main.py` 建议控制在 40 行以内

## Day 2：建立 service 和 repository 边界

### 任务

- [x] 创建 `conversation_repository.py`
- [x] 把会话和消息的数据库读写集中到 repository（数据库操作位置）
- [x] 创建`conversation_service.py`(业务操作位置）
- [x] 修改`conversation_Router`

- [x] 创建`chat_repository.py`
- [ ] 创建 `chat_service.py`
- [ ] 把“创建会话—保存用户消息—读取历史—调用模型—保存回复”移入 service
- [ ] 路由层只处理输入、调用 service、返回输出
- [ ] 定义业务异常，不在 service 中抛 `HTTPException`
- [ ] 在 API 层或全局异常处理器中把业务异常转换成 HTTP 响应

### 只补这些基础

- 函数职责
- 分层架构
- 依赖方向
- 自定义异常
- Python 类型标注

### 验收

- [ ] API 层没有 SQL 或 sqlite3 调用
- [ ] repository 层没有 FastAPI 依赖
- [ ] service 层没有 `HTTPException`
- [ ] 原有接口测试通过

## Day 3：让测试脱离真实模型和真实数据

### 任务

- [ ] 为测试使用独立临时数据库
- [ ] 每个测试之间数据库状态隔离
- [ ] mock 普通 LLM 响应
- [ ] mock 流式 LLM 响应
- [ ] 增加创建会话测试
- [ ] 增加会话列表测试
- [ ] 增加聊天成功测试
- [ ] 增加不存在会话测试
- [ ] 增加 LLM 超时测试
- [ ] 增加流式中断测试

### 只补这些基础

- pytest fixture
- monkeypatch / mock
- 单元测试与集成测试
- 测试数据隔离
- 正常路径与失败路径

### 验收

- [ ] 断网且没有真实 API Key 时也能运行全部测试
- [ ] 测试不会读写开发环境数据库
- [ ] 测试数量不少于 10 个
- [ ] 关键失败路径至少有一个测试

## Day 4：异步边界预备

### 任务

- [ ] 标记项目中所有阻塞 I/O
- [ ] 将非流式模型调用改为 `httpx.AsyncClient`
- [ ] 复用 HTTP client，不为每次请求重复创建连接池
- [ ] 明确 connect/read/write/pool timeout
- [ ] 保留同步 SQLite，记录它为什么仍然是阻塞点
- [ ] 不在本周强行把整个数据库层异步化

### 只补这些基础

- 阻塞 I/O
- `async` / `await`
- event loop
- 连接池
- timeout 分类
- 资源关闭

### 验收

- [ ] 普通聊天接口不使用一次性同步 `httpx.Client`
- [ ] HTTP client 在应用生命周期内正确创建和关闭
- [ ] 超时能够转换成稳定、可测试的应用错误
- [ ] 异步测试或 TestClient 回归测试通过

## Day 5：清理、文档和答辩

### 任务

- [ ] 修复 README 快速开始命令
- [ ] 更新项目目录说明
- [ ] 增加 `.env.example` 使用说明
- [ ] 运行全部测试
- [ ] 检查 Git diff，移除无关修改
- [ ] 写本周重构前后对比
- [ ] 为 v1.1 创建一个清晰提交

### 必须能回答

- 为什么不能把所有接口写在 `main.py`？
- router、service、repository 分别负责什么？
- 为什么 service 不应该抛 `HTTPException`？
- 为什么测试不能调用真实模型？
- 同步 I/O 放进异步接口会发生什么？
- lifespan 适合管理哪些资源？
- 重构为什么必须保持原接口兼容？

## 本周纪律

1. 每天只推进一个边界，不同时换数据库、加 Redis、加登录。
2. 先写或运行回归测试，再移动代码。
3. 可以向 AI 要解释、测试建议和代码审查；第一版核心代码自己写。
4. 每移动一个接口就运行测试，不在最后一天一次性排错。
5. 看不懂的代码不能提交。

## 本周完成定义

- [ ] Day 1～Day 5 全部验收通过
- [ ] `pytest` 全绿
- [ ] 不依赖真实 LLM 运行测试
- [ ] 核心分层能独立解释
- [ ] 完成一次 15 分钟无稿项目讲解
- [ ] Git 工作区无意外文件和密钥
