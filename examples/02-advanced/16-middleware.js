/**
 * 示例 16: SDK 中间件 (Middleware)
 * 
 * 核心价值：全局治理与 AOP (Global Governance)
 * 中间件允许你在请求发送给模型之前，或结果返回给用户之前进行干预。
 * 
 * 常见场景：
 * 1. 注入全局 Prompt（如：始终要求用 Markdown 格式）。
 * 2. 敏感词过滤。
 * 3. 性能监控与自定义日志。
 */

const { generateText, wrapLanguageModel } = require('ai');
const { ollama } = require('ai-sdk-ollama');

async function main() {
  console.log('--- 示例 16: SDK 中间件演示 ---');

  // 1. 定义一个简单的日志中间件
  const loggingMiddleware = {
    wrapLanguageModel: (model) => {
      return wrapLanguageModel({
        model,
        middleware: {
          wrapGenerate: async ({ doGenerate, params, model: modelArg }) => {
            console.log('\n[中间件] 🛰️  正在调用 wrapGenerate...');
            console.log(`[中间件] 目标模型: ${modelArg.modelId}`);
            
            const start = Date.now();
            const result = await doGenerate();
            const duration = Date.now() - start;

            console.log(`[中间件] ✅ 响应已接收，耗时: ${duration}ms`);
            return result;
          }
        }
      });
    }
  };

  // 2. 应用中间件
  const baseModel = ollama('qwen2.5-coder:latest');
  const modelWithMiddleware = loggingMiddleware.wrapLanguageModel(baseModel);

  try {
    const { text } = await generateText({
      model: modelWithMiddleware,
      prompt: '请用一句话赞美一下 JavaScript。',
    });

    console.log('\nAI 回复:', text);
  } catch (error) {
    console.error('执行失败:', error.message);
  }
}

main().catch(console.error);
