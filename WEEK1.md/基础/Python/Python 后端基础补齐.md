# Python 后端基础补齐

1. 类型标注：

   ```bash
   # 基础数据
   name: str = "Tom"
   age: int = 18
   price: float = 9.9
   is_active: bool = True

   # 函数
   def add(a: int, b: int) -> int: # -> 标注返回值
       return a + b
   ```

2. 写 Pydantic 请求模型：

   创建文件`app/schemas/chat.py`:

   ```bash
   from pydantic import BaseModel, Field

   class ChatRequest(BaseModel):
       message: str = Field(..., min_length=1, max_length=2000)
       user_id: int | None = None

   class ChatResponse(BaseModel):
       reply: str
   ```

   代码解释：

   1. `BaseModel`：

      如`class ChatRequest(BaseModel):`​定义一个请求模型，用户请求`/chat`传回 json：

      ```json
      { "message": "你好",  "user_id": 1 }
      ```
   2. `message: str`​:表示`message`必须是字符串，Pydantic 会对数据类型进行校验
   3. `Field(..., min_length=1, max_length=2000)`：

      ```json
      message: str = Field(..., min_length=1, max_length=2000)
      ```

      `...`​表示`message`必填，然后是最少字符与最大字符限制
   4. `user_id: int | None = None`：

      `user_id`​可以为`int`​或`None`​且默认值为`None`

3. 将 Pydantic 模型接入 FastAPI 中：

   修改`app/main.py`:

   1. `from app.schemas.chat import ChatRequest, ChatResponse`
   2. 添加接口：

      ```json
      @app.post("/chat/test", response_model=ChatResponse)
      def chat_test(request: ChatRequest):
          return ChatResponse(
              reply=f"你刚才说的是：{request.message}"
          )
      ```

4. 启动测试：

   打开`docs`​，点击新添加的接口，点击`Try it out`  
   输入测试内容测试
