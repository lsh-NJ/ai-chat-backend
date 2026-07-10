# 使用 FastAPI

1. 在 vscode 中打开当前文件夹的虚拟环境：

   1. `Cmd + Shift + P`
   2. 点击`Python: Select Interpreter`
   3. 输入虚拟环境中 Python 的路径（`./.venv/bin/pythonx.xx`）
2. 创建项目目录结构：

   ```bash
   # mkdir -p 创建文件夹
   mkdir -p app/api app/core app/models app/schemas app/services tests
   # touch 创建空文件
   touch app/main.py .env .gitignore README.md
   # ls 检查结构
   ls
   ```
3. 第一个 FastAPI 接口：

   ```bash
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
   ```

4. 启动 FastAPI：

   ```bash
   uvicorn app.main:app --reload
   ```

   如果启动成功会看到类似：

   ```bash
   Uvicorn running on http://127.0.0.1:8000
   ```

5. 打开浏览器测试：

   在浏览器中打开上方给出的网址应该看到：

   ```bash
   {
     "message": "Welcome to AI Chat Backend"
   }
   ```

   再访问`http://127.0.0.1:8000/health`应该看到：

   ```bash
   {
     "status": "ok",
     "message": "AI Chat Backend is running"
   }
   ```

   访问 **<u>FastAPI 自动生成的接口文件</u>**​ **：**​`http://127.0.0.1:8000/docs`
6. 在`docs`中测试函数接口：

   查看函数接口详情，点击`Try it out`​，编辑输入，点击`Execute`查看输出

‍
