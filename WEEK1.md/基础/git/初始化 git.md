# 初始化 git

1. 填写`.gitignore`文件：

   ```bash
   .venv/
   __pycache__/
   *.pyc
   .env
   .DS_Store
   .idea/
   .vscode/
   ```

   防止本地环境与 apikey 等重要内容上传
2. 将文件夹变为一个 Git 仓库：

   ```bash
   git init
   ```
3. 查看 git 的管理情况：

   ```bash
   git status
   ```

   发现其中并没有 tests 文件夹，这是因为 git 追踪的是文件，tests 目前为空文件夹，直接被 git 无视掉了

‍
