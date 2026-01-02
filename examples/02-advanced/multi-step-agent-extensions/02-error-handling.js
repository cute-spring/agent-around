/**
 * 错误处理示例
 * 演示多步 Agent 中的错误处理、重试和回退机制
 */

const { generateText, tool } = require('ai');
const { ollama } = require('ai-sdk-ollama');
const { z } = require('zod');

class RetryManager {
  constructor(maxRetries = 3, delayMs = 1000) {
    this.maxRetries = maxRetries;
    this.delayMs = delayMs;
  }

  async executeWithRetry(operation, operationName = 'operation') {
    let lastError;
    
    for (let attempt = 1; attempt <= this.maxRetries; attempt++) {
      try {
        console.log(`[${operationName}] 尝试第 ${attempt} 次...`);
        return await operation();
      } catch (error) {
        lastError = error;
        console.warn(`[${operationName}] 第 ${attempt} 次尝试失败:`, error.message);
        
        if (attempt < this.maxRetries) {
          console.log(`等待 ${this.delayMs}ms 后重试...`);
          await this.delay(this.delayMs);
        }
      }
    }
    
    throw new Error(`${operationName} 所有重试均失败: ${lastError.message}`);
  }

  delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

async function errorHandlingDemo() {
  console.log('=== 错误处理示例演示 ===');
  const retryManager = new RetryManager();

  // 模拟不可靠的工具
  const unreliableTools = {
    getExchangeRate: tool({
      description: '获取货币汇率（可能失败）',
      parameters: z.object({
        from: z.string(),
        to: z.string(),
      }),
      execute: async ({ from, to }) => {
        // 模拟随机失败
        if (Math.random() < 0.6) { // 60% 失败率
          throw new Error('汇率服务暂时不可用');
        }
        
        console.log('成功获取汇率');
        return { rate: from === 'USD' && to === 'CNY' ? 7.2 : 1.0 };
      },
    }),

    calculatePrice: tool({
      description: '计算价格（稳定）',
      parameters: z.object({
        price: z.number(),
        taxRate: z.number(),
      }),
      execute: async ({ price, taxRate }) => {
        const total = price * (1 + taxRate);
        return { total };
      },
    }),
  };

  console.log('\n--- 方法1: 工具内部的错误处理 ---');
  try {
    const result = await generateText({
      model: ollama('qwen2.5-coder:latest'),
      maxSteps: 5,
      tools: unreliableTools,
      prompt: '计算100美元商品的人民币含税价格（税率10%）',
    });
    console.log('结果:', result.text);
  } catch (error) {
    console.error('执行失败:', error.message);
  }

  console.log('\n--- 方法2: 带重试的工具包装器 ---');
  await executeWithRetryWrapper();

  console.log('\n--- 方法3: 回退机制 ---');
  await fallbackMechanismDemo();
}

// 方法2: 使用重试包装器
async function executeWithRetryWrapper() {
  const retryManager = new RetryManager(2, 500);

  const reliableTools = {
    getExchangeRate: tool({
      description: '获取货币汇率（带重试）',
      parameters: z.object({
        from: z.string(),
        to: z.string(),
      }),
      execute: async (params) => {
        return await retryManager.executeWithRetry(
          async () => {
            // 模拟可能失败的操作
            if (Math.random() < 0.7) {
              throw new Error('网络请求超时');
            }
            return { rate: 7.2 };
          },
          'getExchangeRate'
        );
      },
    }),
  };

  try {
    const result = await generateText({
      model: ollama('qwen2.5-coder:latest'),
      maxSteps: 3,
      tools: reliableTools,
      prompt: '测试重试机制',
    });
    console.log('带重试的执行结果:', result.text);
  } catch (error) {
    console.error('重试机制执行失败:', error.message);
  }
}

// 方法3: 回退机制
async function fallbackMechanismDemo() {
  const toolsWithFallback = {
    getExchangeRate: tool({
      description: '获取实时汇率（主服务）',
      parameters: z.object({
        from: z.string(),
        to: z.string(),
      }),
      execute: async ({ from, to }) => {
        // 主服务
        console.log('使用主汇率服务...');
        if (Math.random() < 0.5) {
          throw new Error('主汇率服务不可用');
        }
        return { rate: 7.2, source: 'primary' };
      },
    }),

    getExchangeRateFallback: tool({
      description: '获取备用汇率',
      parameters: z.object({
        from: z.string(),
        to: z.string(),
      }),
      execute: async ({ from, to }) => {
        // 备用服务
        console.log('使用备用汇率服务...');
        return { rate: 7.15, source: 'fallback' }; // 备用汇率可能略有不同
      },
    }),

    getCachedExchangeRate: tool({
      description: '获取缓存汇率',
      parameters: z.object({
        from: z.string(),
        to: z.string(),
      }),
      execute: async ({ from, to }) => {
        // 缓存数据
        console.log('使用缓存汇率...');
        return { rate: 7.18, source: 'cache', cached: true };
      },
    }),
  };

  // 智能提示，指导AI使用回退策略
  const smartPrompt = `
请计算100美元兑换成人民币的金额。
按以下优先级获取汇率：
1. 首先尝试 getExchangeRate（实时汇率）
2. 如果失败，尝试 getExchangeRateFallback（备用服务）
3. 最后使用 getCachedExchangeRate（缓存数据）
`;

  try {
    const result = await generateText({
      model: ollama('qwen2.5-coder:latest'),
      maxSteps: 5,
      tools: toolsWithFallback,
      prompt: smartPrompt,
    });
    console.log('回退机制结果:', result.text);
  } catch (error) {
    console.error('回退机制执行失败:', error.message);
  }
}

// 方法4: 全局错误处理
async function globalErrorHandler() {
  console.log('\n--- 方法4: 全局错误处理 ---');
  
  try {
    // 这里可以包装整个 generateText 调用
    const result = await generateText({
      model: ollama('qwen2.5-coder:latest'),
      maxSteps: 3,
      tools: {
        riskyOperation: tool({
          description: '高风险操作',
          parameters: z.object({}),
          execute: async () => {
            throw new Error('操作失败');
          },
        }),
      },
      prompt: '执行高风险操作',
    });
    
    console.log('成功:', result.text);
  } catch (error) {
    console.error('全局捕获错误:', error.message);
    // 这里可以记录日志、发送通知等
  }
}

module.exports = { errorHandlingDemo, RetryManager };

if (require.main === module) {
  errorHandlingDemo().catch(console.error);
}