/**
 * 示例 23: Mem0 Graph Memory (知识图谱) 与 Vercel AI SDK 集成
 * 
 * 场景：处理复杂的多跳推理 (Multi-hop Reasoning)
 * 知识图谱能够存储 实体 (Entities) 和 关系 (Relations)，而不仅仅是片段。
 * 例如：Alice 属于 项目A，项目A 使用 技术B -> Alice 间接关联 技术B。
 */

const { Memory } = require('mem0ai/oss');
const { generateText } = require('ai');
const { ollama } = require('ai-sdk-ollama');
require('dotenv').config();

class GraphMemoryAgent {
  constructor() {
    this.memory = new Memory({
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
        provider: "memory",
        config: {
          collectionName: "graph-reasoning-demo",
          dimension: 768, // 明确指定 nomic-embed-text 的维度
        }
      }
    });
  }

  /**
   * 模拟多步知识注入
   */
  async seedKnowledge() {
    console.log('🏗️  正在构建知识图谱关系...');
    
    const facts = [
      "Alice 是 Apollo 项目的负责人。",
      "Bob 是 Apollo 项目的高级后端工程师。",
      "Bob 精通 Node.js 和分布式系统。",
      "Charlie 是项目 Artemis 的前端负责人。",
      "Artemis 项目正在从 React 迁移到 Vue。"
    ];

    for (const fact of facts) {
      console.log(`  - 注入事实: ${fact}`);
      // OSS 版要求使用 userId, agentId 或 runId
      await this.memory.add(fact, { userId: "system_graph" });
    }
    console.log('✅ 知识注入完成。\n');
  }

  /**
   * 执行带有图谱推理能力的对话
   */
  async chat(userInput) {
    // 搜索相关知识
    const relevantMemories = await this.memory.search(userInput, { userId: "system_graph", limit: 10 });
    console.log('DEBUG: relevantMemories type:', typeof relevantMemories, Array.isArray(relevantMemories));
    console.log('DEBUG: relevantMemories:', JSON.stringify(relevantMemories, null, 2));
    
    // 适配 OSS 返回格式
    const memoriesArray = Array.isArray(relevantMemories) ? relevantMemories : (relevantMemories.results || []);
    const context = memoriesArray.map(m => m.memory || m.content).join('\n');

    console.log('🔍 检索到的关联上下文:');
    relevantMemories.forEach(m => console.log(`   -> ${m.memory || m.content}`));

    const systemPrompt = `你是一个具备图谱推理能力的 AI 助手。
你的任务是根据提供的片段信息，进行“多跳推理”。
例如，如果 A 在项目 X，项目 X 使用技术 Y，那么 A 可能了解技术 Y。

已知事实库：
${context}

请基于上述逻辑回答用户问题。如果信息不足，请说明。`;

    const result = await generateText({
      model: ollama('qwen2.5-coder:latest'),
      system: systemPrompt,
      prompt: userInput,
    });

    return result.text;
  }
}

async function main() {
  console.log('--- Mem0 Graph Memory 多跳推理演示 ---');
  
  const agent = new GraphMemoryAgent();
  
  await agent.seedKnowledge();

  const questions = [
    "Alice 如果遇到了 Node.js 性能瓶颈，她应该在团队里找谁咨询？",
    "Artemis 项目最近在技术栈上有什么大动作？负责人是谁？"
  ];

  for (const q of questions) {
    console.log(`\n[User]: ${q}`);
    const response = await agent.chat(q);
    console.log(`[Assistant]: ${response}`);
  }
}

main().catch(console.error);
