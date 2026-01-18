/**
 * 集中管理 AI Provider 配置
 * 核心价值：DRY (Don't Repeat Yourself)
 */

import dotenv from 'dotenv';
import { ollama } from 'ai-sdk-ollama';
import { createOpenAI } from '@ai-sdk/openai';

dotenv.config();

// --- 1. Provider 策略定义 (Strategy Pattern) ---
const PROVIDER_STRATEGIES = {
  'ollama': (config) => {
    return ollama(config.modelId);
  },
  
  'openai-compatible': (config) => {
    const provider = createOpenAI({
      apiKey: process.env[config.apiKeyEnv] || '',
      baseURL: config.baseURL,
      compatibility: 'compatible'
    });
    return provider.chat(config.modelId);
  },
  
  'azure': (config) => {
    // 动态导入，避免在未安装相关包时报错
    return import('@ai-sdk/azure').then(({ createAzure }) => {
      const azureOptions = {
        resourceName: config.resourceName || process.env.AZURE_RESOURCE_NAME,
        deploymentName: config.deploymentName || config.modelId,
      };
      if (config.tokenProvider) {
        azureOptions.tokenProvider = config.tokenProvider;
      } else {
        azureOptions.apiKey = process.env[config.apiKeyEnv] || process.env.AZURE_API_KEY;
      }
      return createAzure(azureOptions)(config.modelId);
    });
  },
  
  'google': (config) => {
    return import('@ai-sdk/google').then(({ createGoogleGenerativeAI }) => {
      const google = createGoogleGenerativeAI({
        apiKey: process.env[config.apiKeyEnv] || process.env.GOOGLE_GENERATIVE_AI_API_KEY,
      });
      return google(config.modelId);
    });
  }
};

// --- 2. 模型注册中心 (Model Registry) ---
let MODELS = [
  {
    id: 'qwen-local',
    name: 'Qwen 2.5 Coder (Local)',
    provider: 'ollama',
    modelId: 'qwen2.5-coder:latest',
    group: 'local'
  },
  {
    id: 'ollama-llama3',
    name: 'Llama 3.2 Vision (Local)',
    provider: 'ollama',
    modelId: 'llama3.2-vision:latest',
    group: 'local'
  },
  {
    id: 'deepseek-chat',
    name: 'DeepSeek Chat',
    provider: 'openai-compatible',
    modelId: 'deepseek-chat',
    baseURL: 'https://api.deepseek.com',
    apiKeyEnv: 'DEEPSEEK_API_KEY',
    group: 'cloud'
  }
];

// --- 3. 核心功能实现 ---

const INSTANCE_CACHE = new Map();

function validateConfig(config) {
  const required = ['id', 'name', 'provider', 'modelId'];
  for (const field of required) {
    if (!config[field]) throw new Error(`Missing required field: ${field}`);
  }
  if (!PROVIDER_STRATEGIES[config.provider]) {
    throw new Error(`Unsupported provider: ${config.provider}`);
  }
}

export function registerModel(config) {
  validateConfig(config);
  const exists = MODELS.find(m => m.id === config.id);
  if (exists) {
    MODELS = MODELS.map(m => m.id === config.id ? { ...m, ...config } : m);
  } else {
    MODELS.push(config);
  }
  INSTANCE_CACHE.delete(config.id);
}

export function registerProvider(type, strategyFn) {
  PROVIDER_STRATEGIES[type] = strategyFn;
}

export function MODEL_REGISTRY() {
  return MODELS;
}

export async function getModelInstance(modelId) {
  if (INSTANCE_CACHE.has(modelId)) {
    return INSTANCE_CACHE.get(modelId);
  }

  const config = MODELS.find(m => m.id === modelId);
  if (!config) throw new Error(`Model ${modelId} not found in registry`);

  const strategy = PROVIDER_STRATEGIES[config.provider];
  if (!strategy) throw new Error(`Provider strategy ${config.provider} not found`);

  try {
    const instance = await strategy(config);
    INSTANCE_CACHE.set(modelId, instance);
    return instance;
  } catch (e) {
    throw new Error(`Failed to initialize ${modelId} (${config.provider}): ${e.message}`);
  }
}
