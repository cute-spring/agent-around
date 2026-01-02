/**
 * 示例 25: SDK 基础设施级可靠性 (Load Balancing & Fallback)
 * 
 * 【设计模式：外层兜底 (Outer Layer Reliability)】
 * 相比于 04-threshold-fallback-routing.js 解决的“业务意图不确定性”，
 * 本示例展示如何利用 Vercel AI SDK 的原生能力解决“基础设施不可靠性”。
 * 
 * 1. experimental_fallback: 当主模型不可用（如 429 限流、500 报错）时，自动切换到备用模型。
 * 2. experimental_loadBalance: 在多个 Provider 之间分配流量，优化吞吐量并规避单一 Provider 的速率限制。
 */

const { generateText } = require('ai');
const { openai } = require('@ai-sdk/openai');
const { ollama } = require('ai-sdk-ollama');
require('dotenv').config();

// 模拟 Fallback 逻辑
async function fallback(models) {
  return {
    type: 'fallback',
    models,
    execute: async (options) => {
      let lastError;
      for (const model of models) {
        try {
          return await generateText({ ...options, model });
        } catch (error) {
          lastError = error;
          console.log(`⚠️  模型 ${model.modelId || 'unknown'} 失败，尝试下一个...`);
        }
      }
      throw lastError;
    }
  };
}

// 模拟 LoadBalance 逻辑
function loadBalance(models) {
  return {
    type: 'load-balance',
    models,
    getNext: () => models[Math.floor(Math.random() * models.length)]
  };
}

/**
 * 场景 1: 自动容灾 (Automatic Fallback)
 */
async function runFallbackDemo() {
  console.log('\n--- [场景 1] 执行自动容灾策略 (Fallback) ---');
  
  const modelSequence = [
    openai('gpt-4o'),           // 主模型 (云端)
    ollama('qwen2.5:0.5b')      // 备用模型 (本地轻量级模型，响应极快)
  ];

  try {
    // 模拟 fallback 行为
    let result;
    for (const model of modelSequence) {
      try {
        console.log(`正在尝试使用: ${model.modelId}`);
        result = await generateText({
          model: model,
          prompt: '请解释什么是“混沌工程”？',
        });
        break; 
      } catch (error) {
        console.log(`⚠️  模型 ${model.modelId} 失败: ${error.message}`);
      }
    }

    if (result) {
      console.log('✅ 响应结果:', result.text.slice(0, 100) + '...');
    }
  } catch (error) {
    console.error('❌ 即使有 Fallback 还是失败了:', error.message);
  }
}

/**
 * 场景 2: 负载均衡 (Load Balancing)
 */
async function runLoadBalanceDemo() {
  console.log('\n--- [场景 2] 执行负载均衡策略 (Load Balance) ---');

  const instances = [
    ollama('qwen2.5:0.5b'),
    ollama('gemma3:1b')
  ];

  try {
    const selected = instances[Math.floor(Math.random() * instances.length)];
    console.log(`负载均衡选中实例: ${selected.modelId}`);
    
    const { text } = await generateText({
      model: selected,
      prompt: '如何实现高可用的 AI 服务架构？',
    });

    console.log('✅ 响应结果:', text.slice(0, 100) + '...');
  } catch (error) {
    console.error('❌ 负载均衡执行出错:', error.message);
  }
}

/**
 * 场景 3: 组合拳 (Hybrid Reliability)
 */
async function runHybridReliabilityDemo() {
  console.log('\n--- [场景 3] 混合高可用架构 (Load Balance + Fallback) ---');

  // 1. 定义负载均衡组
  const lbGroup = [openai('gpt-4o'), openai('gpt-4o-2024-05-13')];
  
  // 2. 定义容灾序列
  const fallbackSequence = [
    () => lbGroup[Math.floor(Math.random() * lbGroup.length)], // 优先从 LB 组选
    () => ollama('qwen2.5:0.5b') // 最后保底
  ];

  try {
    let result;
    for (const getModel of fallbackSequence) {
      const model = getModel();
      try {
        console.log(`正在尝试执行层级: ${model.modelId}`);
        result = await generateText({
          model: model,
          prompt: '简述 AI 应用的可靠性设计。',
        });
        break;
      } catch (error) {
        console.log(`⚠️  该层级失败，触发 Fallback...`);
      }
    }

    if (result) {
      console.log('✅ 混合模式响应:', result.text.slice(0, 100) + '...');
    }
  } catch (error) {
    console.error('❌ 极端情况：所有层级均失效', error.message);
  }
}

async function main() {
  console.log('🚀 开始展示 SDK 基础设施级可靠性方案...');
  
  await runFallbackDemo();
  await runLoadBalanceDemo();
  await runHybridReliabilityDemo();

  console.log('\n💡 总结：');
  console.log('- Fallback 解决了“活不活得下来”的问题。');
  console.log('- Load Balance 解决了“撑不撑得住”的问题。');
  console.log('- 它们与 04-threshold-routing 结合，才能构成真正的企业级 Agent 架构。');
}

main().catch(err => {
  console.error('运行演示时发生错误:', err);
});
