/**
 * 示例 12: OpenAI 兼容模式 (智谱 AI / Zhipu AI)
 * 
 * 核心价值：生态复用 (Ecosystem Reuse)
 * Vercel AI SDK 的 openai 提供者支持自定义 baseURL。
 * 这意味着你可以用同样的代码调用任何支持 OpenAI 格式的云端大模型，
 * 无需安装额外的 SDK，只需更改配置。
 */

require('dotenv').config();
const { generateText } = require('ai');
const { createOpenAI } = require('@ai-sdk/openai');

// 1. 创建一个兼容 OpenAI 格式的自定义提供者实例
const zhipu = createOpenAI({
  apiKey: process.env.ZHIPU_API_KEY,
  baseURL: process.env.ZHIPU_BASE_URL,
  compatibility: 'compatible', // 强制使用 Chat Completions API，避免调用不支持的 /responses 接口
});

async function main() {
  console.log('--- 示例 12: 调用 OpenAI 兼容接口 (智谱 AI) ---');

  if (!process.env.ZHIPU_API_KEY || process.env.ZHIPU_API_KEY.includes('your_zhipu')) {
    console.error('错误: 请先在 .env 文件中设置有效的 ZHIPU_API_KEY');
    return;
  }

  try {
    const { text } = await generateText({
      model: zhipu.chat('glm-4-flash'), // 使用 .chat() 确保调用 Chat Completions 接口
      prompt: '请用一段富有诗意的文字描述人工智能的未来。',
    });

    console.log('\n--- 智谱 AI 回复 ---');
    console.log(text);
  } catch (error) {
    console.error('调用失败:', error.message);
  }
}

main().catch(console.error);
