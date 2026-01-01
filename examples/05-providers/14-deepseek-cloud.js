/**
 * 示例 14: DeepSeek 官方 API 支持
 * 
 * 核心价值：直接使用 DeepSeek 官方高性能接口
 * 通过 @ai-sdk/openai 的兼容模式，我们可以无缝集成 DeepSeek。
 * 支持 deepseek-chat (普通对话) 和 deepseek-reasoner (深度思考/R1)。
 */

const { generateText } = require('ai');
const { cloud } = require('../../lib/ai-providers');

async function main() {
  console.log('--- 示例 14: 调用 DeepSeek 官方 API ---');

  if (!process.env.DEEPSEEK_API_KEY || process.env.DEEPSEEK_API_KEY.includes('your_deepseek')) {
    console.warn('⚠️ 提示: 请先在 .env 文件中设置有效的 DEEPSEEK_API_KEY');
    console.log('您可以从 https://platform.deepseek.com/ 获取 API Key');
    return;
  }

  try {
    console.log('\n正在调用 deepseek-chat (普通模型)...');
    const { text: chatText } = await generateText({
      model: cloud.deepseek,
      prompt: '简单介绍一下 DeepSeek 的优势。',
    });
    console.log('\n--- DeepSeek Chat 回复 ---');
    console.log(chatText);

    console.log('\n-----------------------------------');
    console.log('正在调用 deepseek-reasoner (R1 深度思考模型)...');
    
    const { text: reasoningText, reasoningText: rawReasoning } = await generateText({
      model: cloud.deepseekReasoning,
      prompt: '为什么 0.1 + 0.2 不等于 0.3？请深入分析。',
    });

    if (rawReasoning) {
      console.log('\n--- 🧠 思考过程 ---');
      console.log(rawReasoning);
    }

    console.log('\n--- ✨ 最终回答 ---');
    console.log(reasoningText);

  } catch (error) {
    console.error('调用失败:', error.message);
    if (error.message.includes('401')) {
      console.error('认证失败：请检查 DEEPSEEK_API_KEY 是否正确。');
    }
  }
}

main().catch(console.error);
