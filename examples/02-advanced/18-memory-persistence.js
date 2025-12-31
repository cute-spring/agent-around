/**
 * 示例 18: 对话记忆持久化 (Memory Persistence)
 * 
 * 核心原理：
 * LLM 本身是无状态的。为了让 Agent 能够“记住”之前的对话，我们需要：
 * 1. 维护一个消息数组 (Messages Array)；
 * 2. 在每次对话结束时，将该数组序列化为 JSON 并保存到磁盘；
 * 3. 在下次启动时，读取该 JSON 文件并恢复消息历史；
 * 4. 每次调用 generateText 时，将完整的历史记录作为 context 传入。
 */
const { generateText } = require('ai');
const { ollama } = require('ai-sdk-ollama');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

// 定义记忆文件存储路径
const MEMORY_FILE = path.join(__dirname, '../../data/chat_memory.json');

/**
 * 确保数据存储目录存在
 */
function ensureDataDir() {
  const dir = path.dirname(MEMORY_FILE);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

/**
 * 从本地文件加载历史消息
 */
function loadMessages() {
  if (fs.existsSync(MEMORY_FILE)) {
    try {
      const data = fs.readFileSync(MEMORY_FILE, 'utf8');
      return JSON.parse(data);
    } catch (e) {
      console.error('加载记忆文件失败:', e);
    }
  }
  return [];
}

/**
 * 将历史消息保存到本地文件
 */
function saveMessages(messages) {
  ensureDataDir();
  fs.writeFileSync(MEMORY_FILE, JSON.stringify(messages, null, 2));
}

/**
 * 核心对话逻辑：加载历史 -> 加入新消息 -> 生成回复 -> 保存历史
 */
async function chat(userInput) {
  console.log(`\n用户: ${userInput}`);

  // 1. 加载已有历史（恢复上下文）
  let messages = loadMessages();
  
  // 2. 将当前用户的输入加入队列
  messages.push({ role: 'user', content: userInput });

  // 3. 调用模型，传入完整历史（这是“记忆”的关键）
  const result = await generateText({
    model: ollama('qwen2.5-coder:latest'),
    messages,
  });

  const assistantResponse = result.text;
  console.log(`助手: ${assistantResponse}`);

  // 4. 将助手的回复也存入历史，以维持对话连贯性
  messages.push({ role: 'assistant', content: assistantResponse });

  // 5. 持久化到磁盘，确保程序关闭后记忆不丢失
  saveMessages(messages);
  console.log(`\n[系统] 对话记忆已同步至: ${path.basename(MEMORY_FILE)}`);
}

async function main() {
  console.log('--- 记忆持久化 Agent 演示 ---');
  console.log('即使多次运行，Agent 也能通过本地文件记住您的名字和偏好。\n');

  const history = loadMessages();
  
  if (history.length === 0) {
    // 第一次运行：建立记忆
    await chat('你好，我叫 Gavin，我非常喜欢使用 Node.js 进行开发。');
  } else {
    // 后续运行：验证记忆
    console.log(`[系统] 成功加载历史记录（共 ${history.length} 条消息）。`);
    await chat('你还记得我叫什么名字，以及我喜欢什么吗？');
  }
}

main().catch(console.error);
