/**
 * 示例 9: 消耗统计 (Token Usage & Metadata)
 * 
 * 核心价值：内置的观测与统计 (Built-in Observability)
 * 在生产环境中，监控 Token 消耗和性能至关重要。
 * SDK 在结果中直接返回了详尽的统计信息，无需你手动计算或拦截响应头。
 */

const { generateText } = require('ai');
const { ollama } = require('ai-sdk-ollama');

async function main() {
  console.log('--- 示例 9: Token 消耗统计演示 ---');

  const result = await generateText({
    model: ollama('qwen2.5-coder:latest'),
    prompt: '用 50 字左右解释什么是量子纠缠。',
  });

  // 核心价值：直接从结果对象中获取 usage 信息
  const { usage, finishReason, warnings } = result;

  console.log('\nAI 回复:', result.text);
  console.log('\n--- 统计信息 ---');
  console.log(`提示词 Tokens (Prompt): ${usage.inputTokens}`);
  console.log(`生成回复 Tokens (Completion): ${usage.outputTokens}`);
  console.log(`总 Tokens (Total): ${usage.totalTokens}`);
  console.log(`结束原因: ${finishReason}`); // 例如 'stop' 表示正常结束

  if (warnings && warnings.length > 0) {
    console.log('警告信息:', warnings);
  }
}

main().catch(console.error);
