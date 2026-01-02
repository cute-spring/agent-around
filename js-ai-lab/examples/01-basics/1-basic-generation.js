/**
 * 示例 1: 基础文本生成 (Basic Generation)
 * 
 * 核心价值：Provider Agnostic (供应商无关性)
 * 重构说明：此文件已改为从 ../../lib/ai-providers 加载配置。
 */

const { generateText } = require('ai');
const { local } = require('../../lib/ai-providers');

async function main() {
  console.log('--- 示例 1: 统一 API 调用 ---');

  // 直接使用配置好的本地模型
  const { text } = await generateText({
    model: local.chat, 
    prompt: '用一句话介绍 Vercel AI SDK 的最大优势。',
  });

  console.log('AI 回复:', text);
}

main().catch(console.error);
