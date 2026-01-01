/**
 * 方案 2: 结构化 LLM 决策路由 (Structured LLM Dispatcher)
 * 
 * 【原因】
 * 当路由逻辑非常复杂（如需要理解复杂的商业条款、判断用户情绪、或根据多条规则综合决策）时，传统的关键词或向量匹配难以胜任。
 * 
 * 【目标】
 * 利用大模型的推理能力进行逻辑分类，并强制要求模型返回结构化数据（JSON），以便下游程序处理。
 * 
 * 【结果】
 * 1. 能够处理极其复杂的意图识别（如咨询批量折扣）。
 * 2. 通过 Zod Schema 保证了输出的 100% 可解析性。
 * 
 * 【可进一步提升的地方】
 * 1. 使用更轻量、针对路由微调过的小模型（如 RouterBERT 或经过 SFT 的 Qwen-1.5B）来降低延迟和成本。
 * 2. 结合 RAG 动态注入最新的部门职责说明，使路由逻辑具备“热更新”能力。
 */
const { generateObject } = require('ai');
const { ollama } = require('ai-sdk-ollama');
const { z } = require('zod');
require('dotenv').config();

async function llmRouter(input) {
  console.log(`\n--- 分析意图: "${input}" ---`);

  const { object: decision } = await generateObject({
    model: ollama('qwen2.5-coder:latest'),
    schema: z.object({
      route: z.enum(['TECHNICAL', 'BILLING', 'SALES']).describe('目标路由'),
      reason: z.string().describe('分类原因'),
      confidence: z.number().min(0).max(100).describe('置信度 (0-100)')
    }),
    system: `你是一个专业的企业客服中转系统。请分析用户的输入并分发到正确的部门。
    
    Few-shot 示例：
    用户输入："我上周付过款了，为什么发票还没开出来？" -> 路由：BILLING
    用户输入："软件在启动时提示权限不足" -> 路由：TECHNICAL
    用户输入："我想咨询一下针对 100 人团队的定价方案" -> 路由：SALES
    
    请确保 confidence 字段是一个 0 到 100 之间的整数。`,
    prompt: input,
  });

  console.log(`[决策结果] 路由至: ${decision.route}`);
  console.log(`[原因摘要] ${decision.reason}`);
  console.log(`[置信评分] ${decision.confidence}`);
  
  return decision;
}

async function main() {
  console.log('--- 企业级方案 2: LLM 决策路由 (结构化输出版) ---');
  await llmRouter('你们的产品很棒，但我想知道批量购买有没有折扣？');
  await llmRouter('我上周付过款了，为什么发票还没开出来？');
}

main().catch(console.error);
