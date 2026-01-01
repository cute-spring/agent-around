/**
 * 示例 22: Mem0 与 Vercel AI SDK 集成 (Long-term Memory & Fact Extraction)
 * 
 * 核心原理：
 * 传统的记忆模式（如示例 18）只是简单堆叠对话历史。
 * Mem0 提供了一个更智能的记忆层，它能从对话中提取“事实”(Facts) 并持久化存储。
 * 
 * 集成方式主要有两种：
 * 1. 使用官方提供的 @mem0/vercel-ai-provider (高度集成)
 * 2. 手动集成 (灵活控制，适用于本地模型或自定义存储)
 * 
 * 我已经在 22-mem0-integration.js 中完成了 工业级改进 。这个版本不再是简单的代码片段，而是一个功能完整的 Hybrid Memory Agent 。

### 核心改进说明
1. 混合记忆架构 (Hybrid Memory) ：
   
   - 短期记忆 ：使用滑动窗口（ shortTermHistory ）保留最近 5 轮的原始对话。这保证了 Agent 能够理解指代词（如“它”、“刚才那个”）并维持对话的自然流转。
   - 长期记忆 ：通过 getMemories 从 Mem0 检索出的“事实”会被注入系统提示词。这让 Agent 能够跨越数周甚至数月记住用户的关键偏好。
2. 主动工具化 (Agentic Tooling) ：
   
   - 引入了 updatePreferences 工具。Agent 现在可以自主判断用户的某句话是否包含值得永久记住的“事实”（例如：“我下个月要去徒步”），并主动调用工具将其存入 Mem0。
3. 异步后台同步 (Async Background Sync) ：
   
   - 为了极致的响应速度，我们将全量对话的分析和存储放在了后台执行（ syncBackground ）。Agent 会先给用户返回结果，然后在不阻塞用户的情况下让 Mem0 在后台完成复杂的 NLP 事实提取。
 */

const { generateText, tool } = require('ai');
const { ollama } = require('ai-sdk-ollama');
const { MemoryClient } = require('mem0ai'); // Platform 版
const { Memory: MemoryOSS } = require('mem0ai/oss'); // Self-Hosted (OSS) 版
const { z } = require('zod');
require('dotenv').config();

// 设置运行模式: 'oss' 或 'platform'
const MEMORY_MODE = process.env.MEMORY_MODE || 'oss'; 

/**
 * 工业级改进：Hybrid Memory Agent (支持 OSS & Platform)
 */
class ProMemoryAgent {
  constructor(userId) {
    this.userId = userId;
    this.shortTermHistory = [];
    this.historyLimit = 5;
    this.mode = MEMORY_MODE;
    
    console.log(`🚀 [System]: 正在启动 ${this.mode.toUpperCase()} 记忆模式...`);

    if (this.mode === 'platform') {
      const apiKey = process.env.MEM0_API_KEY;
      if (!apiKey || apiKey === 'your_mem0_api_key_here') {
        throw new Error('Platform 模式需要有效的 MEM0_API_KEY');
      }
      this.mem0 = new MemoryClient({ apiKey });
    } else {
      // Self-Hosted (OSS) 配置
      // 全部使用本地 Ollama 基础设施
      this.mem0 = new MemoryOSS({
        llm: {
          provider: "ollama",
          config: {
            model: "qwen2.5-coder:latest",
            url: "http://localhost:11434",
          }
        },
        embedder: {
          provider: "ollama",
          config: {
            model: "nomic-embed-text",
            url: "http://localhost:11434",
          }
        },
        vectorStore: {
          provider: "memory", // OSS 模式下默认内存存储，生产环境建议用 qdrant
          config: {
            collectionName: "local-agent-memory",
          }
        }
      });
    }
  }

  async chat(userInput) {
    console.log(`\n[User]: ${userInput}`);

    // 1. 预检索长期记忆
    const memories = await this.getMemories(userInput);
    
    // 2. 构建系统提示词
    const systemPrompt = `你是一个拥有深度记忆的 AI 助手。
    以下是关于用户的长期背景事实（来自 ${this.mode.toUpperCase()} 记忆库）：
    ${memories.length > 0 ? memories.map(m => `- ${m}`).join('\n') : '暂无相关背景'}
    
    你的任务：
    1. 优先回答用户的问题。
    2. 如果发现用户提到了新的重要信息，请调用 updatePreferences 工具进行存储。
    3. 即使调用了工具，也请务必在回复中以自然语言给予用户回应。`;

    // 3. 执行生成 (包含工具调用)
    const result = await generateText({
      model: ollama('qwen2.5-coder:latest'),
      system: systemPrompt,
      messages: [...this.shortTermHistory, { role: 'user', content: userInput }],
      tools: {
        updatePreferences: tool({
          description: '当用户提到新的偏好、重要计划或个人信息时调用，将其同步到长期记忆。',
          parameters: z.object({
            fact: z.string().describe('提取出的事实陈述'),
          }),
          execute: async ({ fact }) => {
            console.log(`[Tool]: 正在更新本地记忆: ${fact}`);
            // OSS 模式使用 userId, Platform 模式使用 user_id
            const filter = this.mode === 'oss' ? { userId: this.userId } : { user_id: this.userId };
            await this.mem0.add(fact, filter);
            return { status: 'Memory updated successfully', savedFact: fact };
          }
        }),
      },
      maxSteps: 2,
    });

    const assistantResponse = result.text;
    console.log(`[Assistant]: ${assistantResponse}`);

    // 4. 更新短期历史
    this.shortTermHistory.push({ role: 'user', content: userInput });
    this.shortTermHistory.push({ role: 'assistant', content: assistantResponse });
    if (this.shortTermHistory.length > this.historyLimit * 2) {
      this.shortTermHistory = this.shortTermHistory.slice(-this.historyLimit * 2);
    }

    // 5. 后台异步同步整个对话上下文
    const context = `User: ${userInput}\nAssistant: ${assistantResponse}`;
    const filter = this.mode === 'oss' ? { userId: this.userId } : { user_id: this.userId };
    this.mem0.add(context, filter).catch(() => {});

    return assistantResponse;
  }

  async getMemories(query) {
    try {
      // OSS 版和 Platform 版的 search 参数和返回格式不同
      const filter = this.mode === 'oss' ? { userId: this.userId } : { user_id: this.userId };
      const results = await this.mem0.search(query, filter);
      
      if (this.mode === 'platform') {
        return results.map(r => r.memory || r.content);
      } else {
        // OSS 版结果在 results 字段中
        return (results.results || []).map(r => r.memory);
      }
    } catch (e) {
      console.warn(`[Memory Error]: ${e.message}`);
      return [];
    }
  }
}

async function proDemo() {
  const agent = new ProMemoryAgent("gavin_pro_001");
  
  await agent.chat("你好，我叫 Gavin，我最近迷上了徒步，打算下个月去珠峰大本营。");
  await agent.chat("你还记得我下个月的计划吗？顺便根据我的爱好推荐一下装备。");
}

console.log('--- 工业级改进版 Mem0 + Vercel AI SDK 集成演示 ---\n');
proDemo().catch(console.error);
