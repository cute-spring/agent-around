/**
 * 状态管理示例
 * 演示多步 Agent 执行过程中的状态跟踪和管理
 */

const { generateText, tool } = require('ai');
const { ollama } = require('ai-sdk-ollama');
const { z } = require('zod');

class ExecutionState {
  constructor() {
    this.state = new Map();
    this.executionHistory = [];
    this.startTime = Date.now();
  }

  set(key, value) {
    this.state.set(key, value);
    this.log(`状态更新: ${key} = ${JSON.stringify(value)}`);
  }

  get(key) {
    return this.state.get(key);
  }

  log(message, data = null) {
    const entry = {
      timestamp: new Date().toISOString(),
      elapsed: Date.now() - this.startTime,
      message,
      data
    };
    this.executionHistory.push(entry);
    console.log(`[状态日志] ${message}`);
  }

  getHistory() {
    return this.executionHistory;
  }

  getSummary() {
    return {
      totalSteps: this.executionHistory.length,
      duration: Date.now() - this.startTime,
      state: Object.fromEntries(this.state),
      history: this.executionHistory
    };
  }
}

async function stateManagementDemo() {
  console.log('=== 状态管理示例演示 ===');
  const state = new ExecutionState();

  const stateAwareTools = {
    calculatePrice: tool({
      description: '计算商品含税价格',
      parameters: z.object({
        price: z.number(),
        taxRate: z.number(),
      }),
      execute: async ({ price, taxRate }) => {
        state.log('开始计算价格', { price, taxRate });
        
        const total = price * (1 + taxRate);
        state.set('taxedPrice', total);
        state.set('currency', 'USD');
        state.set('calculationTime', new Date().toISOString());
        
        state.log('价格计算完成', { total });
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
        state.log('获取汇率', { from, to });
        
        // 检查是否已经计算过价格
        const taxedPrice = state.get('taxedPrice');
        if (!taxedPrice) {
          state.log('警告: 尚未计算价格，但正在获取汇率');
        }
        
        const rate = from === 'USD' && to === 'CNY' ? 7.2 : 1.0;
        state.set('exchangeRate', rate);
        state.set('rateSource', 'api');
        state.set('rateTimestamp', new Date().toISOString());
        
        state.log('汇率获取完成', { rate });
        return { rate };
      },
    }),

    convertCurrency: tool({
      description: '货币转换',
      parameters: z.object({
        amount: z.number(),
        from: z.string(),
        to: z.string(),
      }),
      execute: async ({ amount, from, to }) => {
        state.log('开始货币转换', { amount, from, to });
        
        // 从状态中获取汇率，或使用默认值
        const rate = state.get('exchangeRate') || 
                    (from === 'USD' && to === 'CNY' ? 7.2 : 1.0);
        
        const converted = amount * rate;
        
        // 保存最终结果到状态
        state.set('finalAmount', converted);
        state.set('finalCurrency', to);
        state.set('conversionRate', rate);
        state.set('completionTime', new Date().toISOString());
        
        state.log('货币转换完成', { converted, rate });
        return { converted, currency: to, rate };
      },
    }),

    // 状态查询工具
    getExecutionStatus: tool({
      description: '获取当前执行状态',
      parameters: z.object({}),
      execute: async () => {
        const summary = state.getSummary();
        state.log('状态查询被执行');
        return summary;
      },
    }),
  };

  console.log('\n--- 方法1: 基础状态跟踪 ---');
  try {
    const result = await generateText({
      model: ollama('qwen2.5-coder:latest'),
      maxSteps: 6,
      tools: stateAwareTools,
      prompt: '计算100美元商品的人民币含税价格（税率10%），并显示执行状态',
    });

    console.log('\n最终结果:', result.text);
    console.log('\n=== 执行状态总结 ===');
    console.log(JSON.stringify(state.getSummary(), null, 2));
  } catch (error) {
    console.error('执行失败:', error.message);
    console.log('错误时的状态:', state.getSummary());
  }

  console.log('\n--- 方法2: 持久化状态 ---');
  await persistentStateDemo();

  console.log('\n--- 方法3: 状态验证 ---');
  await stateValidationDemo();
}

// 方法2: 持久化状态
async function persistentStateDemo() {
  console.log('\n演示状态持久化...');
  
  // 模拟从数据库或文件加载状态
  const savedState = {
    taxedPrice: 110,
    currency: 'USD',
    previousExecution: '2024-01-01T10:00:00Z'
  };

  const state = new ExecutionState();
  // 恢复状态
  Object.entries(savedState).forEach(([key, value]) => {
    state.set(key, value);
  });

  state.log('状态恢复完成');

  const tools = {
    continueCalculation: tool({
      description: '继续之前的计算',
      parameters: z.object({
        targetCurrency: z.string(),
      }),
      execute: async ({ targetCurrency }) => {
        const previousPrice = state.get('taxedPrice');
        if (!previousPrice) {
          throw new Error('没有找到之前的价格数据');
        }

        state.log('继续计算', { previousPrice, targetCurrency });
        const rate = targetCurrency === 'CNY' ? 7.2 : 1.0;
        const result = previousPrice * rate;
        
        state.set('continuedResult', result);
        return { result, currency: targetCurrency };
      },
    }),
  };

  const result = await generateText({
    model: ollama('qwen2.5-coder:latest'),
    maxSteps: 2,
    tools,
    prompt: '基于之前的状态继续计算，转换为人民币',
  });

  console.log('继续计算结果:', result.text);
}

// 方法3: 状态验证
async function stateValidationDemo() {
  console.log('\n演示状态验证...');
  
  const state = new ExecutionState();
  
  const validationTools = {
    validateCalculation: tool({
      description: '验证计算结果',
      parameters: z.object({
        expectedResult: z.number(),
        tolerance: z.number().optional().default(0.1),
      }),
      execute: async ({ expectedResult, tolerance }) => {
        const actualResult = state.get('finalAmount');
        
        if (!actualResult) {
          throw new Error('尚未计算出最终结果');
        }
        
        const difference = Math.abs(actualResult - expectedResult);
        const isValid = difference <= tolerance;
        
        state.set('validation', {
          isValid,
          expected: expectedResult,
          actual: actualResult,
          difference,
          tolerance
        });
        
        state.log('验证完成', { isValid, difference });
        return { isValid, difference };
      },
    }),
  };

  // 先执行计算
  const stateTools = {
    calculate: tool({
      description: '简单计算',
      parameters: z.object({
        a: z.number(),
        b: z.number(),
      }),
      execute: async ({ a, b }) => {
        const result = a * b;
        state.set('finalAmount', result);
        return { result };
      },
    }),
  };

  // 合并工具
  const allTools = { ...stateTools, ...validationTools };

  const result = await generateText({
    model: ollama('qwen2.5-coder:latest'),
    maxSteps: 4,
    tools: allTools,
    prompt: '计算 10 * 11，然后验证结果是否接近 110',
  });

  console.log('验证结果:', result.text);
  console.log('最终状态:', JSON.stringify(state.getSummary(), null, 2));
}

module.exports = { stateManagementDemo, ExecutionState };

if (require.main === module) {
  stateManagementDemo().catch(console.error);
}