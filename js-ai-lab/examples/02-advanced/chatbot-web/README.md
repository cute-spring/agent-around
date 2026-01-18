# AI Chatbot Web - ChatGPT Style

这是一个基于原生 JavaScript 和 Express 实现的 ChatGPT 风格的聊天机器人 Web 应用。

## 核心特性

- **多模型支持**：支持本地模型（如 Ollama/Qwen）和云端模型（如 DeepSeek, Azure GPT-4, Google Gemini）。
- **多会话管理**：支持创建、切换、删除不同的对话会话。
- **标题自动生成**：新对话在发送第一条消息后，会自动调用 AI 模型生成一个简短的标题。
- **流式响应**：提供丝滑的打字机式输出体验。
- **Mermaid 渲染**：支持在对话中渲染流程图（Mermaid 语法）。
- **本地持久化**：所有聊天记录以 JSON 文件形式存储在 `js-ai-lab/data/sessions/` 目录下。

## 快速启动

### 1. 环境准备

确保你已经在根目录下配置了 `.env` 文件，包含必要的 API 密钥：

```bash
# 例如：
DEEPSEEK_API_KEY=your_key_here
GOOGLE_GENERATIVE_AI_API_KEY=your_key_here
```

### 2. 安装依赖

在 `js-ai-lab` 根目录下执行：

```bash
npm install
```

### 3. 启动服务

进入应用目录并运行服务器：

```bash
cd examples/02-advanced/chatbot-web
node server.js
```

服务器启动后，控制台会显示：
`Backend server running at http://localhost:3000`

### 4. 访问应用

打开浏览器访问 [http://localhost:3000](http://localhost:3000) 即可开始对话。

## 项目结构

- `server.js`: 后端 Express 服务器，负责 API 路由、模型调用及会话持久化。
- `public/index.html`: 前端单页面应用，包含 UI 布局、Markdown 解析及流式交互逻辑。
- `data/sessions/`: 聊天历史记录存储目录（已加入 .gitignore）。

## 技术栈

- **后端**: [Express](https://expressjs.com/), [Vercel AI SDK](https://sdk.vercel.ai/)
- **前端**: Tailwind CSS, Marked.js (Markdown 解析), Mermaid.js (图表渲染)
