/**
 * 性能优化示例
 * 演示多步 Agent 的性能优化技术和最佳实践
 */

const { generateText, tool } = require('ai');
const { ollama } = require('ai-sdk-ollama');
const { z } = require('zod');

class PerformanceMonitor {
  constructor() {
    this.metrics = {
      toolCalls: 0,
      startTime: Date.now(),
      toolTimings: new Map(),
      totalTokens: 0
    };
  }

  startToolCall(toolName) {
    this.metrics.toolCalls++;
    this.metrics.toolTimings.set(toolName, {
      start: Date.now(),
      end: null,
      duration: null
    });
  }

  endToolCall(toolName) {
    const timing = this.metrics.toolTimings.get(toolName);
    if (timing) {
      timing.end = Date.now();
      timing.duration = timing.end - timing.start;
    }
  }

  addTokenCount(count) {
    this.metrics.totalTokens += count;
  }

  getMetrics() {
    const totalDuration = Date.now() - this.metrics.startTime;
    return {
      ...this.metrics,
      totalDuration,
      averageToolTime: Array.from(this.metrics.toolTimings.values())
        .reduce((sum, t) => sum + (t.duration || 0), 0) / this.metrics.toolCalls
    };
  }
}

async function performanceOptimizationDemo() {
  console.log('=== 性能优化示例演示 ===');
  const monitor = new PerformanceMonitor();

  console.log('\n--- 方法1: 工具调用优化 ---');
  await toolCallOptimization(monitor);

  console.log('\n--- 方法2: 缓存策略 ---');
  await cachingStrategyDemo(monitor);

  console.log('\n--- 方法3: 批量处理 ---');
  await batchProcessingDemo(monitor);

  console.log('\n--- 性能指标报告 ---');
  console.log(JSON.stringify(monitor.getMetrics(), null, 2));
}

// 方法1: 工具调用优化
async function toolCallOptimization(monitor) {
  const optimizedTools = {
    // 轻量级工具 - 快速返回
    getSimpleExchangeRate: tool({
      description: '获取简单汇率（优化版）',
      parameters: z.object({
        from: z.string(),
        to: z.string(),
      }),
      execute: async ({ from, to }) => {
        monitor.startToolCall('getSimpleExchangeRate');
        
        // 快速内存查询，避免网络请求
        const rates = {
          'USD-CNY': 7.2,
          'USD-EUR': 0.92,
          'USD-JPY': 150,
          'CNY-USD': 0.14,
        };
        
        const rate = rates[`${from}-${to}`] || 1.0;
        
        monitor.endToolCall('getSimpleExchangeRate');
        return { rate, source: 'memory-cache' };
      },
    }),

    // 智能工具 - 根据输入选择策略
    smartCalculate: tool({
      description: '智能计算（根据复杂度选择算法）',
      parameters: z.object({
        numbers: z.array(z.number()),
        operation: z.enum(['sum', 'average', 'max', 'min']),
      }),
      execute: async ({ numbers, operation }) => {
        monitor.startToolCall('smartCalculate');
        
        let result;
        
        // 根据数据量选择算法
        if (numbers.length > 1000) {
          // 大数据量优化算法
          result = performOptimizedCalculation(numbers, operation);
        } else {
          // 小数据量直接计算
          result = performSimpleCalculation(numbers, operation);
        }
        
        monitor.endToolCall('smartCalculate');
        return { result };
      },
    }),
  };

  try {
    const result = await generateText({
      model: ollama('qwen2.5-coder:latest'),
      maxSteps: 3,
      tools: optimizedTools,
      prompt: '计算100美元兑换成人民币，使用优化工具',
    });
    console.log('优化工具结果:', result.text);
  } catch (error) {
    console.error('优化工具执行失败:', error.message);
  }
}

// 方法2: 缓存策略
async function cachingStrategyDemo(monitor) {
  const cache = new Map();
  
  const cachingTools = {
    getCachedExchangeRate: tool({
      description: '获取带缓存的汇率',
      parameters: z.object({
        from: z.string(),
        to: z.string(),
        forceRefresh: z.boolean().optional().default(false),
      }),
      execute: async ({ from, to, forceRefresh }) => {
        monitor.startToolCall('getCachedExchangeRate');
        
        const cacheKey = `${from}-${to}`;
        
        // 检查缓存
        if (!forceRefresh && cache.has(cacheKey)) {
          const cached = cache.get(cacheKey);
          monitor.endToolCall('getCachedExchangeRate');
          return { ...cached, cached: true, timestamp: new Date().toISOString() };
        }
        
        // 模拟API调用（较慢）
        await simulateDelay(200);
        
        const rates = {
          'USD-CNY': 7.2,
          'USD-EUR': 0.92,
        };
        
        const rate = rates[cacheKey] || 1.0;
        const result = { rate, source: 'api', cached: false };
        
        // 更新缓存
        cache.set(cacheKey, result);
        
        monitor.endToolCall('getCachedExchangeRate');
        return result;
      },
    }),

    clearCache: tool({
      description: '清空汇率缓存',
      parameters: z.object({}),
      execute: async () => {
        monitor.startToolCall('clearCache');
        cache.clear();
        monitor.endToolCall('clearCache');
        return { cleared: true, cacheSize: 0 };
      },
    }),
  };

  // 第一次调用（会调用API）
  console.log('第一次调用（无缓存）...');
  const result1 = await generateText({
    model: ollama('qwen2.5-coder:latest'),
    maxSteps: 2,
    tools: cachingTools,
    prompt: '获取USD到CNY的汇率',
  });

  // 第二次调用（使用缓存）
  console.log('第二次调用（使用缓存）...');
  const result2 = await generateText({
    model: ollama('qwen2.5-coder:latest'),
    maxSteps: 2,
    tools: cachingTools,
    prompt: '再次获取USD到CNY的汇率',
  });

  console.log('第一次结果:', result1.text);
  console.log('第二次结果:', result2.text);
  console.log('缓存大小:', cache.size);
}

// 方法3: 批量处理
async function batchProcessingDemo(monitor) {
  const batchTools = {
    batchCalculatePrices: tool({
      description: '批量计算价格（高效处理多个项目）',
      parameters: z.object({
        items: z.array(z.object({
          price: z.number(),
          taxRate: z.number(),
          currency: z.string(),
        })),
      }),
      execute: async ({ items }) => {
        monitor.startToolCall('batchCalculatePrices');
        
        // 批量处理（比单个处理更高效）
        const results = items.map(item => ({
          total: item.price * (1 + item.taxRate),
          currency: item.currency,
          originalPrice: item.price
        }));
        
        monitor.endToolCall('batchCalculatePrices');
        return { results, processedCount: items.length };
      },
    }),

    multiCurrencyConvert: tool({
      description: '多货币批量转换',
      parameters: z.object({
        conversions: z.array(z.object({
          amount: z.number(),
          from: z.string(),
          to: z.string(),
        })),
      }),
      execute: async ({ conversions }) => {
        monitor.startToolCall('multiCurrencyConvert');
        
        const rates = {
          'USD-CNY': 7.2,
          'EUR-USD': 1.09,
          'JPY-USD': 0.0067,
        };
        
        const results = conversions.map(conv => {
          const rate = rates[`${conv.from}-${conv.to}`] || 1.0;
          return {
            original: conv.amount,
            converted: conv.amount * rate,
            from: conv.from,
            to: conv.to,
            rate
          };
        });
        
        monitor.endToolCall('multiCurrencyConvert');
        return { results };
      },
    }),
  };

  try {
    const result = await generateText({
      model: ollama('qwen2.5-coder:latest'),
      maxSteps: 3,
      tools: batchTools,
      prompt: '批量计算：商品A 100美元税率10%，商品B 200欧元税率20%，商品C 5000日元税率8%',
    });
    console.log('批量处理结果:', result.text);
  } catch (error) {
    console.error('批量处理失败:', error.message);
  }
}

// 辅助函数
function performOptimizedCalculation(numbers, operation) {
  // 大数据量优化实现
  switch (operation) {
    case 'sum':
      return numbers.reduce((a, b) => a + b, 0);
    case 'average':
      return numbers.reduce((a, b) => a + b, 0) / numbers.length;
    case 'max':
      return Math.max(...numbers);
    case 'min':
      return Math.min(...numbers);
    default:
      return 0;
  }
}

function performSimpleCalculation(numbers, operation) {
  // 简单实现
  return performOptimizedCalculation(numbers, operation);
}

function simulateDelay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// 方法4: 提前终止优化
async function earlyTerminationDemo() {
  console.log('\n--- 方法4: 提前终止 ---');
  
  const tools = {
    checkFeasibility: tool({
      description: '检查计算可行性',
      parameters: z.object({
        amount: z.number(),
        currency: z.string(),
      }),
      execute: async ({ amount, currency }) => {
        // 如果金额太大或货币不支持，提前终止
        if (amount > 1000000) {
          return { feasible: false, reason: '金额过大' };
        }
        if (!['USD', 'EUR', 'CNY'].includes(currency)) {
          return { feasible: false, reason: '不支持的货币' };
        }
        return { feasible: true };
      },
    }),
  };

  const result = await generateText({
    model: ollama('qwen2.5-coder:latest'),
    maxSteps: 2,
    tools,
    prompt: '检查1000000000美元转换的可行性',
  });
  
  console.log('提前终止检查:', result.text);
}

module.exports = { performanceOptimizationDemo, PerformanceMonitor };

if (require.main === module) {
  performanceOptimizationDemo().catch(console.error);
}