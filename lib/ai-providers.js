/**
 * 集中管理 AI Provider 配置
 * 核心价值：DRY (Don't Repeat Yourself)
 */

require('dotenv').config();
const { ollama } = require('ai-sdk-ollama');
const { createOpenAI } = require('@ai-sdk/openai');

// 1. 本地 Ollama 配置
const localProviders = {
  chat: ollama('qwen2.5-coder:latest'),
  vision: ollama('llama3.2-vision:11b'),
  embedding: ollama.embeddingModel('nomic-embed-text:latest'),
  // 辅助函数用于快速获取特定模型
  model: (name) => ollama(name),
};

// 2. 云端智谱 AI 配置 (OpenAI 兼容模式)
const zhipuProvider = createOpenAI({
  apiKey: process.env.ZHIPU_API_KEY,
  baseURL: 'https://open.bigmodel.cn/api/paas/v4/',
});

// 3. DeepSeek 官方 Provider (使用 OpenAI 兼容模式以确保与 AI SDK v6 兼容)
const deepseekProvider = createOpenAI({
  apiKey: process.env.DEEPSEEK_API_KEY ?? '',
  baseURL: 'https://api.deepseek.com',
  compatibility: 'compatible',
});

const cloudProviders = {
  zhipu: zhipuProvider.chat('glm-4-flash'),
  deepseek: deepseekProvider.chat('deepseek-chat'),
  deepseekReasoning: deepseekProvider.chat('deepseek-reasoner'),
  // 暴露原始 provider 以便自定义使用
  zhipuFactory: zhipuProvider,
  deepseekFactory: deepseekProvider,
};

module.exports = {
  local: localProviders,
  cloud: cloudProviders,
};
