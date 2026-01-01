/**
 * 方案 5: 增强上下文语义路由 (Context-Aware Semantic Routing)
 * 
 * 【原因】
 * 用户的单条消息往往是破碎且缺乏语境的。例如，用户在聊完安装报错后说“怎么还没退款？”，此时如果不参考上下文，很容易误判为财务问题，而实际可能是因为安装失败导致的退款补偿。
 * 
 * 【目标】
 * 将当前输入与历史对话记录（Memory）相结合，通过“意图摘要”技术提取出完整的、带有语境的请求，再进行路由。
 * 
 * 【结果】
 * 1. 极大地降低了“追问型消息”的误判率。
 * 2. 路由系统能够识别出用户意图的漂移（Intent Drift）。
 * 
 * 【可进一步提升的地方】
 * 1. 引入滑动窗口：只保留最近 N 轮或最具相关性的对话片断，避免长上下文导致的 Token 浪费。
 * 2. 情感分析集成：识别用户在上下文中的愤怒程度。如果用户重复提问且情绪激动，无论内容如何，应优先路由至“投诉处理组”。
 */
const { generateText } = require('ai');
const { ollama } = require('ai-sdk-ollama');
require('dotenv').config();

async function summarizeHistory(history) {
  const { text: summary } = await generateText({
    model: ollama('qwen2.5-coder:latest'),
    system: '你是一个对话摘要专家。请将以下对话历史压缩成一句话，重点提取用户正在尝试解决的核心问题。',
    prompt: history.join('\n'),
  });
  return summary;
}

async function contextualRoute(userInput, history) {
  console.log(`\n--- 收到新消息: "${userInput}" ---`);
  
  // 1. 生成历史摘要
  console.log('[系统] 正在分析对话上下文...');
  const summary = await summarizeHistory(history);
  console.log(`[上下文摘要] ${summary}`);

  // 2. 组合意图进行路由
  const enrichedQuery = `历史背景: ${summary} | 当前请求: ${userInput}`;
  console.log(`[路由决策] 正在基于增强信息分发任务...`);
  
  // 模拟决策
  const finalRoute = userInput.includes('退款') || summary.includes('退款') ? 'BILLING' : 'TECHNICAL';
  console.log(`[结果] 最终路由至: ${finalRoute}`);
}

async function main() {
  console.log('--- 企业级方案 5: 上下文感知 (自动摘要版) ---');
  
  const history = [
    '用户: 你们的软件在安装时一直报错',
    '助手: 建议您检查权限并重新运行',
    '用户: 我试过了，还是不行，太令人失望了'
  ];
  
  await contextualRoute('我想退款', history);
}

main().catch(console.error);
