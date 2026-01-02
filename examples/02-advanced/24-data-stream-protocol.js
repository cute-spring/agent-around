/**
 * 示例 24: 增强型流式协议 (Data Stream Protocol)
 * 
 * 核心价值：多通道数据同步 (Multi-channel Data Synchronization)
 * 
 * 在真实的 AI 应用中，你不仅仅需要向前端发送“文本”。
 * 你可能还需要发送：
 * 1. 引用来源 (Sources/Citations)
 * 2. 建议的问题 (Follow-up Questions)
 * 3. 工具执行的中间状态 (Agent Status)
 * 4. 自定义业务数据 (Metadata)
 * 
 * Vercel AI SDK 的 Data Stream Protocol 允许你在同一个 HTTP 流中，
 * 以“数据帧”的形式并行发送模型生成的文本和自定义数据。
 */

const { streamText } = require('ai');
const { ollama } = require('ai-sdk-ollama');

async function main() {
  console.log('--- 示例 24: 增强型流式协议演示 ---');

  try {
    const result = await streamText({
      model: ollama('qwen2.5-coder:latest'),
      prompt: '请用一段话告诉我关于量子计算的一个核心概念，并给出一些参考来源。',
    });

    console.log('\n[协议解析演示] 正在模拟前端接收流...\n');

    // 3. 模拟 Data Stream Protocol 帧
    // 在 Node.js 环境中，我们手动消费 textStream 并模拟协议包装
    // 注意：在真实的 Next.js 环境中，你会直接使用 toDataStreamResponse()
    
    let fullText = '';
    
    // 发送初始数据帧
    const initialData = { type: 'status', message: '正在初始化模型...', model: 'qwen2.5-coder' };
    console.log(`d:${JSON.stringify(initialData)}`);

    for await (const textPart of result.textStream) {
      fullText += textPart;
      // 模拟文本帧: 0:"..."
      process.stdout.write(`0:${JSON.stringify(textPart)}\n`);
    }

    // 发送结束后的数据帧
    const finalData = { 
      type: 'suggestions', 
      questions: ['量子纠缠是如何工作的？'] 
    };
    console.log(`\nd:${JSON.stringify(finalData)}`);

    // 发送结束控制帧
    console.log(`e:{"finishReason":"stop"}`);

    console.log('\n\n--- 最终生成的文本 ---');
    console.log(fullText);

  } catch (error) {
    console.error('执行失败:', error.message);
  }
}

main().catch(console.error);
