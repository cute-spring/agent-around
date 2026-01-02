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

// 4. Azure OpenAI 配置 (可选)
// const { createAzure } = require('@ai-sdk/azure');
// const azureProvider = createAzure({
//   resourceName: process.env.AZURE_RESOURCE_NAME,
//   apiKey: process.env.AZURE_API_KEY,
// });

// 5. Google Gemini 配置 (可选)
// const { createGoogleGenerativeAI } = require('@ai-sdk/google');
// const googleProvider = createGoogleGenerativeAI({
//   apiKey: process.env.GOOGLE_GENERATIVE_AI_API_KEY,
// });

const cloudProviders = {
  zhipu: zhipuProvider.chat('glm-4-flash'),
  deepseek: deepseekProvider.chat('deepseek-chat'),
  deepseekReasoning: deepseekProvider.chat('deepseek-reasoner'),
  // azure: azureProvider('gpt-4o'), // 需要安装 @ai-sdk/azure
  // gemini: googleProvider('gemini-1.5-flash'), // 需要安装 @ai-sdk/google
  // 暴露原始 provider 以便自定义使用
  zhipuFactory: zhipuProvider,
  deepseekFactory: deepseekProvider,
};

module.exports = {
  local: localProviders,
  cloud: cloudProviders,
};
