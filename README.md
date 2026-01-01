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
- [1-basic-generation.js](./examples/01-basics/1-basic-generation.js): 基础文本生成。
- [2-streaming.js](./examples/01-basics/2-streaming.js): 极简流式输出。
- [3-structured-output.js](./examples/01-basics/3-structured-output.js): 配合 Zod 的强类型 JSON 生成。

### 02. 进阶 Agent (Advanced)
- [4-tool-calling.js](./examples/02-advanced/4-tool-calling.js): 基础工具调用。
- [6-multi-step-agent.js](./examples/02-advanced/6-multi-step-agent.js): **自主 Agent**，自动处理“思考-执行”闭环。
- [11-collaborative-agents.js](./examples/02-advanced/11-collaborative-agents.js): 多模型流水线协作（Writer + Reviewer）。
- [14-reasoning-deepseek.js](./examples/02-advanced/14-reasoning-deepseek.js): **深度思考**，提取 DeepSeek-R1 的思考过程。
- [15-mcp-integration.js](./examples/02-advanced/15-mcp-integration.js): **MCP 协议集成**，实现工具动态转换与手动调用回退机制。
- [16-middleware.js](./examples/02-advanced/16-middleware.js): **SDK 中间件**，实现 AOP 全局拦截与治理。
- [17-human-in-the-loop.js](./examples/02-advanced/17-human-in-the-loop.js): **人工介入 (HITL)**，在执行敏感工具前请求人工确认。
- [18-memory-persistence.js](./examples/02-advanced/18-memory-persistence.js): **记忆持久化**，将对话上下文保存至本地文件以实现跨会话记忆。
- [19-semantic-routing.js](./examples/02-advanced/19-semantic-routing.js): **语义路由**，利用向量相似度将用户请求精准分发至不同的处理逻辑。
- [20-supervisor-orchestration.js](./examples/02-advanced/20-supervisor-orchestration.js): **中控调度**，动态分配任务给专门的 Worker Agent。
- [21-self-reflection-coding.js](./examples/02-advanced/21-self-reflection-coding.js): **自我反思**，通过多轮迭代提高生成质量。

#### 🛡️ 路由专项：企业级分发模式 (Enterprise Routing)
> 这是一个完整的路由模式演进体系，展示了从规则匹配到混合语义路由的演进过程。详见 [策略分析文档](./examples/02-advanced/enterprise-routing/STRATEGIES_ANALYSIS.md)。

- [01-hybrid-routing.js](./examples/02-advanced/enterprise-routing/01-hybrid-routing.js): **混合分层路由**，结合 Regex 极速层与向量深度层。
- [02-llm-router.js](./examples/02-advanced/enterprise-routing/02-llm-router.js): **结构化 LLM 决策**，利用 LLM 推理能力进行高精度分类。
- [03-hierarchical-routing.js](./examples/02-advanced/enterprise-routing/03-hierarchical-routing.js): **层级化路由**，实现从“领域 -> 子任务”的逐级精细化分发。
- [04-threshold-fallback-routing.js](./examples/02-advanced/enterprise-routing/04-threshold-fallback-routing.js): **置信度阈值与兜底**，在语义不确定时自动回退至 LLM 或人工。
- [05-contextual-routing.js](./examples/02-advanced/enterprise-routing/05-contextual-routing.js): **上下文感知路由**，根据历史对话状态动态调整分发逻辑。
- [06-semantic-cache-routing.js](./examples/02-advanced/enterprise-routing/06-semantic-cache-routing.js): **语义缓存路由**，利用相似度匹配实现毫秒级快速响应。
- [07-routing-evaluation.js](./examples/02-advanced/enterprise-routing/07-routing-evaluation.js): **路由评估系统**，量化分析不同策略的准确率与延迟。

### 03. 多模态 (Multimodal)
- [7-vision-multimodal.js](./examples/03-multimodal/7-vision-multimodal.js): 视觉图片分析。

### 04. RAG 与向量 (RAG & Embeddings)
- [8-embeddings.js](./examples/04-rag/8-embeddings.js): 文本向量化。
- [10-semantic-similarity.js](./examples/04-rag/10-semantic-similarity.js): 语义相似度计算。

### 05. 多供应商集成 (Providers)
- [12-openai-compatible.js](./examples/05-providers/12-openai-compatible.js): 调用智谱 AI 等 OpenAI 兼容云端模型。
- [13-hybrid-cloud-local.js](./examples/05-providers/13-hybrid-cloud-local.js): **混合架构**，同时使用本地与云端模型。

### 06. 可观测性 (Observability)
- [9-token-usage.js](./examples/06-observability/9-token-usage.js): Token 消耗统计。

## 📂 运行示例

进入对应目录并运行：
```bash
node examples/01-basics/1-basic-generation.js
```

---
*由 AI 助手协助重构，旨在提供更清晰的开发参考。*
