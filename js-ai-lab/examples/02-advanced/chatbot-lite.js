/**
 * 示例: 基于 @ai-sdk 的轻量级本地 Chatbot
 * 
 * 核心特性：
 * 1. 多 Session 持久化：每个对话独立存储在 data/sessions 下。
 * 2. 多模型切换：支持本地 Ollama 和云端模型。
 * 3. 流式响应：提供丝滑的打字机体验。
 * 4. 自动上下文管理：自动加载历史记录。
 */

const { streamText } = require('ai');
const { local, cloud } = require('../../lib/ai-providers');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

const SESSIONS_DIR = path.join(__dirname, '../../data/sessions');

/**
 * 简单的持久化助手
 */
const Persistence = {
  getFilePath: (sessionId) => path.join(SESSIONS_DIR, `${sessionId}.json`),

  load: (sessionId) => {
    const filePath = Persistence.getFilePath(sessionId);
    if (fs.existsSync(filePath)) {
      return JSON.parse(fs.readFileSync(filePath, 'utf8'));
    }
    return [];
  },

  save: (sessionId, messages) => {
    if (!fs.existsSync(SESSIONS_DIR)) {
      fs.mkdirSync(SESSIONS_DIR, { recursive: true });
    }
    fs.writeFileSync(Persistence.getFilePath(sessionId), JSON.stringify(messages, null, 2));
  }
};

/**
 * 核心 Chatbot 函数
 * @param {string} sessionId - 会话 ID
 * @param {string} userInput - 用户输入
 * @param {Object} model - 选择的模型实例 (来自 ai-providers.js)
 */
async function runChatbot(sessionId, userInput, model = local.chat) {
  console.log(`\n[Session: ${sessionId}]`);
  console.log(`[Model: ${model.modelId}]`);
  console.log(`User: ${userInput}`);

  // 1. 加载历史消息
  let messages = Persistence.load(sessionId);
  
  // 2. 添加新消息
  messages.push({ role: 'user', content: userInput });

  // 3. 开始流式生成
  process.stdout.write('AI: ');
  const result = await streamText({
    model: model,
    messages: messages,
    onFinish: ({ text }) => {
      // 4. 对话完成后，保存包含 AI 回复的历史
      messages.push({ role: 'assistant', content: text });
      Persistence.save(sessionId, messages);
      console.log(`\n\n[系统] 对话已保存至 ${sessionId}.json`);
    },
  });

  // 将流输出到控制台
  for await (const textPart of result.textStream) {
    process.stdout.write(textPart);
  }
}

/**
 * 演示运行
 */
async function main() {
  const SESSION_1 = 'project-discussion';
  const SESSION_2 = 'coding-help';

  console.log('--- 启动轻量级 Chatbot 演示 ---');

  // 场景 1: 使用本地模型进行项目讨论
  await runChatbot(SESSION_1, '你好，我想讨论一下我们的 Agent 项目架构。', local.chat);

  // 场景 2: 使用云端模型 (DeepSeek) 寻求代码帮助
  // 注意：需要确保 .env 中配置了 DEEPSEEK_API_KEY
  if (process.env.DEEPSEEK_API_KEY) {
    await runChatbot(SESSION_2, '如何使用 TypeScript 实现一个简单的单例模式？', cloud.deepseek);
  } else {
    console.log('\n[提示] 未检测到 DEEPSEEK_API_KEY，场景 2 将跳过或使用本地模型。');
    await runChatbot(SESSION_2, '如何使用 TypeScript 实现一个简单的单例模式？', local.chat);
  }
}

main().catch(console.error);
