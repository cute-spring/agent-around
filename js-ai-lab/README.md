# JS AI Lab

这是一个用于探索和学习 JavaScript AI 开发的实验项目。

## 项目结构

- `examples/`: 包含各种 AI 开发示例。
    - `01-basics/`: 基础生成、流式输出、结构化输出。
    - `02-advanced/`:
        - `chatbot-web/`: **重点推荐** - 完整的 ChatGPT 风格 Web 应用。
        - `enterprise-routing/`: 企业级模型路由策略。
        - `multi-step-agent-extensions/`: 复杂 Agent 状态管理。
- `lib/`: 通用的 AI Provider 封装，支持多模型注册。
- `data/`: 存放本地会话和持久化数据。

## 快速开始：Chatbot Web

项目中最完整的示例是 `chatbot-web`。

### 启动步骤

1. **安装依赖**:
   ```bash
   npm install
   ```

2. **配置环境变量**:
   在根目录下创建 `.env` 文件，并参考 `.env.example` 填写 API 密钥。

3. **运行服务**:
   ```bash
   cd examples/02-advanced/chatbot-web
   node server.js
   ```

4. **访问**:
   [http://localhost:3000](http://localhost:3000)

更多详细信息请参阅 [chatbot-web README](examples/02-advanced/chatbot-web/README.md)。
