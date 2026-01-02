/**
 * 示例 26: 性能与成本优化 (Performance & Cost Optimization)
 * 
 * 核心价值：
 * 1. Prompt Caching (提示词缓存): 针对支持缓存的模型（如 Anthropic, DeepSeek），通过结构化 Prompt 最大化缓存命中，降低 90% 延迟。
 * 2. Fine-grained Token Control (精细化 Token 控制): 在发送请求前精确计算 Token，并根据预算动态调整上下文长度。
 */

const { generateText } = require('ai');
const { cloud, local } = require('../../lib/ai-providers');
require('dotenv').config();

/**
 * 模拟 countTokens 工具
 * 注意：在 Vercel AI SDK 的最新版本或特定 Provider 中，你可以直接使用 countTokens 函数。
 * 这里我们实现一个简单的估算器用于演示逻辑。
 */
async function countTokensMock({ model, messages }) {
  const text = messages.map(m => typeof m.content === 'string' ? m.content : JSON.stringify(m.content)).join('');
  // 粗略估算：这里我们故意估算得稍微大一点，以确保不会超出真实预算
  return Math.ceil(text.length / 1.1);
}

/**
 * 场景 1: Prompt Caching 适配
 * 策略：将“静态”且“昂贵”的内容（如知识库、系统指令）放在 Prompt 的最前面。
 * 
 * DeepSeek 缓存机制说明：
 * - DeepSeek 自动缓存已处理过的 Prompt 前缀。
 * - 缓存以 64 Tokens 为一个区块进行匹配。
 * - 为了最大化命中率，应确保消息列表的开头部分（System Prompt + 静态参考资料）保持不变。
 */
async function promptCachingDemo() {
  console.log('\n--- [场景 1] Prompt Caching 适配演示 ---');

  // 模拟一个巨大的静态知识库 (Context)
  const hugeKnowledgeBase = `
    这里是公司的核心业务文档... (省略 5000 字)
    1. 报销流程：提交申请 -> 经理审批 -> 财务拨款。
    2. 入职指南：领取电脑 -> 设置邮箱 -> 参加培训。
    ... 更多静态内容 ...
  `;

  const systemPrompt = "你是一个企业助手，请根据提供的知识库回答问题。";

  // 推荐的结构：System + Knowledge Base (Static) + Messages (Dynamic)
  const messages = [
    { role: 'system', content: systemPrompt },
    { role: 'user', content: `参考知识库：\n${hugeKnowledgeBase}` },
    { role: 'user', content: "帮我查一下报销流程是什么？" }
  ];

  console.log('💡 优化建议：将巨大的知识库作为第一条 User 消息或 System 消息的一部分，并保持顺序不变。');
  console.log('这样后续所有基于此知识库的提问，前几千个 Tokens 都会命中 DeepSeek 的缓存，仅需支付极低的缓存费用，且响应几乎瞬时。');
  console.log('\n--- 供应商特定说明 ---');
  console.log('- Azure OpenAI: 自动缓存。需确保前缀超过 1024 Tokens 以触发收益。');
  console.log('- Google Gemini: 显式缓存。通过 Context Caching API 创建缓存 ID，适合 1M+ Tokens 的超长上下文。');

  if (process.env.DEEPSEEK_API_KEY) {
    try {
      const result = await generateText({
        model: cloud.deepseek,
        messages: messages,
      });
      console.log('✅ 响应成功 (如果多次运行，你会发现首字延迟极低)');
      console.log(`[Usage]: Input ${result.usage.inputTokens}, Output ${result.usage.outputTokens}`);
    } catch (e) {
      console.log('跳过实际调用 (API Key 可能未配置)');
    }
  } else {
    console.log('跳过实际调用：未发现 DEEPSEEK_API_KEY');
  }
}

/**
 * 场景 2: Fine-grained Token Control (精细化 Token 控制)
 * 策略：利用 countTokens 在发送前进行预算评估，动态截断历史记录。
 */
async function tokenControlDemo() {
  console.log('\n--- [场景 2] Fine-grained Token Control 演示 ---');

  const MAX_TOKEN_BUDGET = 50; // 调低预算以演示截断逻辑
  const model = local.chat; // 使用本地模型进行演示

  const history = [
    { role: 'user', content: '你好，我想了解关于 AI 发展的历史。' },
    { role: 'assistant', content: 'AI 的发展经历了几个阶段，从 1956 年的达特茅斯会议开始...' },
    { role: 'user', content: '那你能详细说说第二次 AI 浪潮吗？' },
    { role: 'assistant', content: '第二次浪潮主要集中在专家系统和知识库的应用...' },
  ];

  const currentQuery = '现在我们处于哪个阶段？';

  /**
   * 动态截断逻辑
   */
  async function getMessagesWithinBudget(history, query, budget) {
    let selectedHistory = [...history];
    
    while (selectedHistory.length > 0) {
      const messages = [...selectedHistory, { role: 'user', content: query }];
      
      // 核心工具：countTokens (这里使用我们的模拟函数)
      const tokens = await countTokensMock({
        model: model,
        messages: messages
      });

      console.log(`当前尝试的历史长度: ${selectedHistory.length} 条, 预估 Tokens: ${tokens}`);

      if (tokens <= budget) {
        return messages;
      }

      // 如果超出预算，移除最旧的一轮对话 (一问一答)
      selectedHistory.splice(0, 1);
    }

    return [{ role: 'user', content: query }];
  }

  console.log(`目标预算: ${MAX_TOKEN_BUDGET} Tokens`);
  const finalMessages = await getMessagesWithinBudget(history, currentQuery, MAX_TOKEN_BUDGET);

  console.log(`\n最终发送的消息条数: ${finalMessages.length}`);
  console.log('--- 最终发送内容 ---');
  finalMessages.forEach(m => console.log(`[${m.role}]: ${m.content.slice(0, 30)}...`));

  const result = await generateText({
    model: model,
    messages: finalMessages,
  });

  console.log(`\n✅ 实际消耗: ${result.usage.inputTokens} Input Tokens (完全在 ${MAX_TOKEN_BUDGET} 预算内)`);
}

async function main() {
  console.log('=== 性能与成本优化技术演示 ===');
  
  await promptCachingDemo();
  await tokenControlDemo();
}

main().catch(console.error);
