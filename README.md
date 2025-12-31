# Vercel AI SDK 本地实验室 (Ollama 版)

这是一个基于 Vercel AI SDK 和 Ollama 本地模型的模式库 (Pattern Library)。项目已经过模块化重构，方便开发者快速查阅和复用。

## 🚀 核心架构

- **分类目录**: 按照功能逻辑组织示例代码，从基础到进阶一目了然。
- **配置中心**: `lib/ai-providers.js` 统一管理所有本地与云端模型的初始化。
- **混合云/地**: 无缝组合本地隐私与云端大模型算力。

## 🛠️ 环境准备

1. **安装 Ollama**: [下载并安装 Ollama](https://ollama.com/)
2. **下载必要模型**:
   ```bash
   ollama pull qwen2.5-coder:latest
   ollama pull llama3.2-vision:11b
   ollama pull nomic-embed-text
   ```
3. **配置 .env**:
   复制 `.env.example` 为 `.env` 并填写您的云端 API Key（如智谱 AI）。

## 📖 示例指南

### 01. 基础能力 (Basics)
- [1-basic-generation.js](file:///Users/gavinzhang/ws-ai-recharge-2026/agent-around/examples/01-basics/1-basic-generation.js): 基础文本生成。
- [2-streaming.js](file:///Users/gavinzhang/ws-ai-recharge-2026/agent-around/examples/01-basics/2-streaming.js): 极简流式输出。
- [3-structured-output.js](file:///Users/gavinzhang/ws-ai-recharge-2026/agent-around/examples/01-basics/3-structured-output.js): 配合 Zod 的强类型 JSON 生成。

### 02. 进阶 Agent (Advanced)
- [4-tool-calling.js](file:///Users/gavinzhang/ws-ai-recharge-2026/agent-around/examples/02-advanced/4-tool-calling.js): 基础工具调用。
- [6-multi-step-agent.js](file:///Users/gavinzhang/ws-ai-recharge-2026/agent-around/examples/02-advanced/6-multi-step-agent.js): **自主 Agent**，自动处理“思考-执行”闭环。
- [11-collaborative-agents.js](file:///Users/gavinzhang/ws-ai-recharge-2026/agent-around/examples/02-advanced/11-collaborative-agents.js): 多模型流水线协作（Writer + Reviewer）。
- [14-reasoning-deepseek.js](file:///Users/gavinzhang/ws-ai-recharge-2026/agent-around/examples/02-advanced/14-reasoning-deepseek.js): **深度思考**，提取 DeepSeek-R1 的思考过程。
- [15-mcp-integration.js](file:///Users/gavinzhang/ws-ai-recharge-2026/agent-around/examples/02-advanced/15-mcp-integration.js): **MCP 协议集成**，实现工具动态转换与手动调用回退机制。
- [16-middleware.js](file:///Users/gavinzhang/ws-ai-recharge-2026/agent-around/examples/02-advanced/16-middleware.js): **SDK 中间件**，实现 AOP 全局拦截与治理。
- [17-human-in-the-loop.js](file:///Users/gavinzhang/ws-ai-recharge-2026/agent-around/examples/02-advanced/17-human-in-the-loop.js): **人工介入 (HITL)**，在执行敏感工具前请求人工确认。
- [18-memory-persistence.js](file:///Users/gavinzhang/ws-ai-recharge-2026/agent-around/examples/02-advanced/18-memory-persistence.js): **记忆持久化**，将对话上下文保存至本地文件以实现跨会话记忆。
- [19-semantic-routing.js](file:///Users/gavinzhang/ws-ai-recharge-2026/agent-around/examples/02-advanced/19-semantic-routing.js): **语义路由**，利用向量相似度将用户请求精准分发至不同的处理逻辑。

### 03. 多模态 (Multimodal)
- [7-vision-multimodal.js](file:///Users/gavinzhang/ws-ai-recharge-2026/agent-around/examples/03-multimodal/7-vision-multimodal.js): 视觉图片分析。

### 04. RAG 与向量 (RAG & Embeddings)
- [8-embeddings.js](file:///Users/gavinzhang/ws-ai-recharge-2026/agent-around/examples/04-rag/8-embeddings.js): 文本向量化。
- [10-semantic-similarity.js](file:///Users/gavinzhang/ws-ai-recharge-2026/agent-around/examples/04-rag/10-semantic-similarity.js): 语义相似度计算。

### 05. 多供应商集成 (Providers)
- [12-openai-compatible.js](file:///Users/gavinzhang/ws-ai-recharge-2026/agent-around/examples/05-providers/12-openai-compatible.js): 调用智谱 AI 等 OpenAI 兼容云端模型。
- [13-hybrid-cloud-local.js](file:///Users/gavinzhang/ws-ai-recharge-2026/agent-around/examples/05-providers/13-hybrid-cloud-local.js): **混合架构**，同时使用本地与云端模型。

### 06. 可观测性 (Observability)
- [9-token-usage.js](file:///Users/gavinzhang/ws-ai-recharge-2026/agent-around/examples/06-observability/9-token-usage.js): Token 消耗统计。

## 📂 运行示例

进入对应目录并运行：
```bash
node examples/01-basics/1-basic-generation.js
```

---
*由 AI 助手协助重构，旨在提供更清晰的开发参考。*
