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

... (省略部分以保持简洁，实际内容已在之前读取)
