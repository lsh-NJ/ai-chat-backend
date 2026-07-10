# 提交本地 git 仓库

1. 添加所有文件到暂存区：

   ```bash
   git add .
   ```

   使用`git status`检查

2. 提交代码：

   ```bash
   git commit -m "init fastapi project"
   ```

3. 在 GitHub 中创建仓库，获得类似以下命令：

   ```bash
   # 绑定本地仓库到远程仓库
   git remote add origin https://github.com/你的用户名/ai-chat-backend.git
   # 把当前分支命名为 main，-M 为强制命名
   git branch -M main
   # 把本地 main 分支的代码上传到 GitHub 的 origin 仓库
   git push -u origin main
   ```

4. 为 git 配置代理进行推送：

   其中`7890`为设置的代理端口

   ```bash
   git config --global http.proxy http://127.0.0.1:7890
   git config --global https.proxy http://127.0.0.1:7890
   ```
