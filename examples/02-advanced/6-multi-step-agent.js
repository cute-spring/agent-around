/**
 * 示例 6: 自主多步 Agent (Autonomous Multi-step Agent)
 * 
 * 核心价值：自动处理工具循环 (Automatic Tool Loop)
 * 这是 Vercel AI SDK 最独特的价值所在。
 * 在普通的开发中，如果 AI 决定调用工具，你需要手动执行工具，然后把结果再传给 AI。
 * 开启 maxSteps 后，SDK 会自动替你完成这个“思考 -> 执行 -> 再思考”的闭环。
 */

const { generateText, tool } = require('ai');
const { ollama } = require('ai-sdk-ollama');
const { z } = require('zod');

async function main() {
  console.log('--- 示例 6: 自主多步 Agent 演示 ---');

  const result = await generateText({
    model: ollama('qwen2.5-coder:latest'),
    
    // 核心价值：maxSteps。
    // 设置大于 1 的数字后，SDK 会自动处理工具调用结果的返回。
    // AI 可以在一次 generateText 调用中连续完成多个步骤，直到给出最终答案。
    maxSteps: 5, 

    tools: {
      getExchangeRate: tool({
        description: '获取实时货币汇率',
        parameters: z.object({
          from: z.string().describe('源货币代码，如 USD'),
          to: z.string().describe('目标货币代码，如 CNY'),
        }),
        execute: async ({ from, to }) => {
          console.log(`\n[系统执行工具] 正在查询 ${from} 到 ${to} 的汇率...`);
          // 这里可以接入真实的 API
          return { rate: from === 'USD' && to === 'CNY' ? 7.2 : 1.0 };
        },
      }),
      calculatePrice: tool({
        description: '计算商品的含税总价',
        parameters: z.object({
          price: z.number().describe('原价'),
          taxRate: z.number().describe('税率，例如 0.1 表示 10%'),
        }),
        execute: async ({ price, taxRate }) => {
          const total = price * (1 + taxRate);
          console.log(`\n[系统执行工具] 价格计算中: ${price} * (1 + ${taxRate}) = ${total}`);
          return { total };
        },
      }),
    },
    prompt: '一件商品在美国卖 100 美元，税率是 0.1。请帮我计算出它折合人民币的总价是多少？',
  });

  console.log('\n--- 最终计算过程与结论 ---');
  console.log(result.text);
}

main().catch(console.error);
