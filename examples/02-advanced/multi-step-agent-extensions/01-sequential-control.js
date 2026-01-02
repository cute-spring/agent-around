/**
 * 顺序控制示例
 * 演示如何引导或强制 AI 按特定顺序执行工具
 */

const { generateText, tool } = require('ai');
const { ollama } = require('ai-sdk-ollama');
const { z } = require('zod');

async function sequentialControlDemo() {
  console.log('=== 顺序控制示例演示 ===');

  // 方法1: 通过 Prompt Engineering 引导顺序
  const guidedPrompt = `
请按以下顺序执行计算：
1. 首先使用 calculatePrice 计算商品的含税价格
2. 然后使用 getExchangeRate 获取美元兑人民币汇率
3. 最后进行货币转换计算

商品价格：100美元，税率：10%
`;

  // 方法2: 通过工具描述控制顺序
  const sequentialTools = {
    calculatePrice: tool({
      description: '第一步：计算商品的含税总价。必须先调用此工具才能进行后续计算',
      parameters: z.object({
        price: z.number().describe('原价'),
        taxRate: z.number().describe('税率，例如 0.1 表示 10%'),
      }),
      execute: async ({ price, taxRate }) => {
        console.log('\n[执行步骤1] 计算含税价格...');
        const total = price * (1 + taxRate);
        return { total, currency: 'USD' };
      },
    }),

    getExchangeRate: tool({
      description: '第二步：获取货币汇率。必须在 calculatePrice 之后调用，用于货币转换',
      parameters: z.object({
        from: z.string().describe('源货币代码'),
        to: z.string().describe('目标货币代码'),
      }),
      execute: async ({ from, to }) => {
        console.log('\n[执行步骤2] 获取汇率...');
        const rates = {
          'USD-CNY': 7.2,
          'USD-EUR': 0.92,
          'USD-JPY': 150,
        };
        const rate = rates[`${from}-${to}`] || 1.0;
        return { rate };
      },
    }),

    convertCurrency: tool({
      description: '第三步：货币转换。必须在前两个工具完成后调用',
      parameters: z.object({
        amount: z.number().describe('要转换的金额'),
        from: z.string().describe('源货币'),
        to: z.string().describe('目标货币'),
      }),
      execute: async ({ amount, from, to }) => {
        console.log('\n[执行步骤3] 货币转换...');
        // 这里应该调用 getExchangeRate，但为了演示我们直接计算
        const rate = from === 'USD' && to === 'CNY' ? 7.2 : 1.0;
        return { converted: amount * rate, currency: to };
      },
    }),
  };

  console.log('\n--- 方法1: Prompt 引导 ---');
  try {
    const result1 = await generateText({
      model: ollama('qwen2.5-coder:latest'),
      maxSteps: 5,
      tools: sequentialTools,
      prompt: guidedPrompt,
    });
    console.log('最终结果:', result1.text);
    console.log('工具调用历史:', JSON.stringify(result1.toolCalls, null, 2));
  } catch (error) {
    console.error('方法1执行失败:', error.message);
  }

  console.log('\n--- 方法2: 强制顺序执行 ---');
  await forcedSequentialExecution();

  console.log('\n--- 方法4: 混合模式 ---');
  await hybridApproach();
}

// 方法3: 完全手动控制执行顺序
async function forcedSequentialExecution() {
  console.log('\n[强制顺序执行] 手动控制每个步骤...');

  // 步骤1: 计算含税价格
  const priceResult = await calculatePriceManual({ price: 100, taxRate: 0.1 });
  console.log('含税价格:', priceResult.total, priceResult.currency);

  // 步骤2: 获取汇率
  const rateResult = await getExchangeRateManual({ from: 'USD', to: 'CNY' });
  console.log('汇率:', rateResult.rate);

  // 步骤3: 货币转换
  const finalResult = await convertCurrencyManual({
    amount: priceResult.total,
    from: 'USD',
    to: 'CNY'
  });

  console.log('最终人民币价格:', finalResult.converted, finalResult.currency);
  console.log('计算完成！');
}

// 手动执行的工具函数
async function calculatePriceManual({ price, taxRate }) {
  const total = price * (1 + taxRate);
  return { total, currency: 'USD' };
}

async function getExchangeRateManual({ from, to }) {
  const rates = { 'USD-CNY': 7.2 };
  return { rate: rates[`${from}-${to}`] || 1.0 };
}

async function convertCurrencyManual({ amount, from, to }) {
  const rate = from === 'USD' && to === 'CNY' ? 7.2 : 1.0;
  return { converted: amount * rate, currency: to };
}

// 方法4: 混合模式 - AI 决策 + 人工验证
async function hybridApproach() {
  console.log('\n--- 方法4: 混合模式 ---');
  
  const hybridTools = {
    calculatePrice: tool({
      description: '计算商品含税价格',
      parameters: z.object({
        price: z.number(),
        taxRate: z.number(),
      }),
      execute: async ({ price, taxRate }) => {
        const total = price * (1 + taxRate);
        return { total, currency: 'USD' };
      },
    }),
    getExchangeRate: tool({
      description: '获取货币汇率',
      parameters: z.object({
        from: z.string(),
        to: z.string(),
      }),
      execute: async ({ from, to }) => {
        const rate = from === 'USD' && to === 'CNY' ? 7.2 : 1.0;
        return { rate };
      },
    }),
  };

  const result = await generateText({
    model: ollama('qwen2.5-coder:latest'),
    maxSteps: 4,
    tools: hybridTools,
    prompt: '请计算100美元商品的人民币含税价格（税率10%）',
  });

  // 人工验证执行顺序
  console.log('AI 执行过程:', result.text);
  console.log('工具调用历史:', JSON.stringify(result.toolCalls, null, 2));
  console.log('人工验证完成');
}

module.exports = { sequentialControlDemo };

// 执行示例
if (require.main === module) {
  sequentialControlDemo().catch(console.error);
}