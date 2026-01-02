/**
 * 示例 2: 流式传输 (Streaming)
 * 
 * 核心价值：简化流式协议处理 (Simplified Streaming)
 * 在传统的开发中，处理 LLM 的流式输出（SSE）非常痛苦。
 * Vercel AI SDK 将其简化为异步迭代器，让你可以像处理普通循环一样处理流。
 */

const { streamText } = require('ai');
const { ollama } = require('ai-sdk-ollama');

async function main() {
  console.log('--- 示例 2: 极简流式输出 ---');
  
  // streamText 返回一个结果对象，包含 textStream 异步迭代器
  const result = await streamText({
    model: ollama('qwen2.5-coder:latest'),
    prompt: '请写一首关于人工智能的短诗。',
  });

  console.log('正在接收流式回复:');
  
  // 核心价值体现：直接使用 for await 遍历流，无需手动解析 HTTP 协议块
  for await (const textPart of result.textStream) {
    process.stdout.write(textPart);
  }
  
  console.log('\n\n生成完毕！');
}

main().catch(console.error);
