/**
 * 示例 14: 深度思考 (Reasoning / Chain of Thought)
 * 
 * 核心价值：提取 AI 的思考链路 (Extracting the "Why")
 * 像 DeepSeek-R1 或 OpenAI o1 这样的模型会输出思考过程。
 * Vercel AI SDK v6 提供了原生的 `reasoning` 属性，
 * 让你能将“思考过程”与“最终回答”分离，从而在 UI 上实现更优雅的展示（如折叠显示思考过程）。
 */

const { generateText } = require('ai');
const { ollama } = require('ai-sdk-ollama');

async function main() {
  console.log('--- 示例 14: 深度思考提取 (Reasoning) ---');
  console.log('提示：此示例建议配合 deepseek-r1 使用以获得最佳效果。');

  try {
    const result = await generateText({
      // 建议本地运行: ollama run deepseek-r1:latest
      model: ollama('deepseek-r1:latest'),
      prompt: '为什么天空是蓝色的？请先进行深度思考，然后给出简短回答。',
    });

    // 核心价值：SDK 尝试解析并分离 reasoning 文本
    const { text, reasoningText } = result;

    if (reasoningText) {
      console.log('\n--- 🧠 思考过程 (Reasoning) ---');
      console.log(reasoningText);
    } else {
      console.log('\n(提示：当前环境未返回独立的 reasoningText，可能需要 SDK 或模型提供商支持)');
      // 兼容性处理：尝试从文本中手动提取 <think> 标签内容
      const thinkMatch = text.match(/<think>([\s\S]*?)<\/think>/);
      if (thinkMatch) {
        console.log('\n--- 🧠 思考过程 (从文本中提取) ---');
        console.log(thinkMatch[1].trim());
      }
    }

    // 移除文本中的 <think> 部分以获得纯净的回答
    const cleanText = text.replace(/<think>[\s\S]*?<\/think>/, '').trim();

    console.log('\n--- ✨ 最终回答 ---');
    console.log(cleanText);

  } catch (error) {
    console.error('\n执行失败:', error.message);
    console.log('提示: 请确保已安装并启动了 deepseek-r1 模型: ollama run deepseek-r1');
  }
}

main().catch(console.error);
