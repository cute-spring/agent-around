/**
 * 顺序控制示例 - 本地Ollama优化版
 * 核心价值：本地优先 (Local First)
 * 
 * 使用本地Ollama模型替代云端GLM-4，确保可靠性和零成本
 * 保持与lib/ai-providers.js配置的一致性
 */

const { generateText, tool } = require('ai');
const { z } = require('zod');
const { local } = require('../../../lib/ai-providers');
require('dotenv').config();

// 定义针对本地模型优化的工具函数
const localTools = {
  calculatePrice: tool({
    description: 'Calculate total price including tax. Input price and tax rate, return total price and currency.',
    parameters: z.object({ 
      price: z.number().describe('Original price, must be a number'),
      taxRate: z.number().describe('Tax rate as decimal, e.g., 0.1 for 10%')
    }),
    execute: async ({ price, taxRate }) => {
      console.log(`[Local Tool] Calculating taxed price: ${price} * (1 + ${taxRate})`);
      const total = price * (1 + taxRate);
      return { 
        total: parseFloat(total.toFixed(2)), 
        currency: 'USD',
        calculation: `${price} * (1 + ${taxRate}) = ${total.toFixed(2)}`
      };
    }
  }),

  getExchangeRate: tool({
    description: 'Get currency exchange rate. Input source and target currency codes, return exchange rate.',
    parameters: z.object({ 
      from: z.string().describe('Source currency code, 3 letters, e.g., USD'),
      to: z.string().describe('Target currency code, 3 letters, e.g., CNY')
    }),
    execute: async ({ from, to }) => {
      console.log(`[Local Tool] Getting exchange rate: ${from} -> ${to}`);
      const rate = from === 'USD' && to === 'CNY' ? 7.2 : 1.0;
      return { 
        rate: parseFloat(rate.toFixed(2)),
        pair: `${from}/${to}`
      };
    }
  }),

  convertCurrency: tool({
    description: 'Convert currency amount. Input amount and exchange rate, return converted amount and target currency.',
    parameters: z.object({ 
      amount: z.number().describe('Amount to convert, must be a number'),
      rate: z.number().describe('Exchange rate, must be a number')
    }),
    execute: async ({ amount, rate }) => {
      console.log(`[Local Tool] Converting currency: ${amount} * ${rate}`);
      const result = amount * rate;
      return { 
        converted: parseFloat(result.toFixed(2)), 
        currency: 'CNY',
        calculation: `${amount} * ${rate} = ${result.toFixed(2)}`
      };
    }
  })
};

// 针对本地模型优化的英文提示词（qwen2.5-coder对英文响应更好）
const localPrompt = `
You are a financial calculation assistant. Please help me complete the following task:

Task: Calculate the RMB price of a $100 product after adding 10% tax.

Requirements:
1. Execute three steps in strict sequence
2. Use the corresponding tool function for each step
3. Ensure complete parameter provision
4. Use the result from the previous step as input for the next step

Step instructions:
Step 1: Use calculatePrice tool to calculate taxed price
- Parameters: price=100, taxRate=0.1

Step 2: Use getExchangeRate tool to get USD to CNY exchange rate
- Parameters: from="USD", to="CNY"

Step 3: Use convertCurrency tool to convert taxed USD price to RMB
- amount parameter: use result from Step 1
- rate parameter: use result from Step 2

Please ensure each tool call provides correct parameters in the proper format.
`;

// 手动顺序执行（可靠的后备方案）
async function manualExecution() {
  console.log('\n🔧 Starting manual sequential execution...');
  
  try {
    // Step 1: Calculate taxed price
    const priceResult = await localTools.calculatePrice.execute({ price: 100, taxRate: 0.1 });
    console.log(`✅ Taxed price: ${priceResult.total} ${priceResult.currency}`);
    
    // Step 2: Get exchange rate
    const rateResult = await localTools.getExchangeRate.execute({ from: 'USD', to: 'CNY' });
    console.log(`✅ Exchange rate: 1 USD = ${rateResult.rate} CNY`);
    
    // Step 3: Convert currency
    const convertResult = await localTools.convertCurrency.execute({ 
      amount: priceResult.total, 
      rate: rateResult.rate 
    });
    console.log(`✅ Final price: ${convertResult.converted} ${convertResult.currency}`);
    
    return {
      success: true,
      result: `Product RMB price: ${convertResult.converted} CNY`,
      details: { priceResult, rateResult, convertResult }
    };
    
  } catch (error) {
    console.error('Manual execution failed:', error.message);
    return { success: false, error: error.message };
  }
}

async function main() {
  console.log('=== Sequential Control Demo (Local Ollama Edition) ===\n');

  console.log('🚀 Using local Ollama model: qwen2.5-coder\n');

  try {
    console.log('🤖 Attempting AI automatic tool calling...');
    
    const result = await generateText({
      model: local.chat, // 使用lib/ai-providers.js中的统一配置
      maxSteps: 6, // 合理的步数限制
      tools: localTools,
      prompt: localPrompt
    });

    console.log('\n📊 AI generated result:');
    console.log(result.text || '(No text output)');
    
    // 详细分析工具调用情况
    if (result.toolCalls && result.toolCalls.length > 0) {
      console.log('\n🔍 Tool call analysis:');
      
      let successCount = 0;
      result.toolCalls.forEach((call, index) => {
        console.log(`\nStep ${index + 1}: ${call.toolName}`);
        console.log(`   Input: ${JSON.stringify(call.input)}`);
        
        if (call.input && Object.keys(call.input).length > 0) {
          successCount++;
          console.log(`   ✅ Parameters complete`);
        } else {
          console.log(`   ❌ Parameters missing`);
        }
        
        if (call.result) {
          console.log(`   Result: ${JSON.stringify(call.result)}`);
        }
      });
      
      console.log(`\n📈 Success rate: ${successCount}/${result.toolCalls.length}`);
      
      if (successCount === result.toolCalls.length && result.toolCalls.length >= 2) {
        console.log('🎉 Local AI tool calling successful!');
        return;
      }
    }
    
    // 如果AI调用不完美，使用手动方案
    console.log('\n⚠️  AI tool calling needs optimization, switching to manual...');
    const manualResult = await manualExecution();
    
    if (manualResult.success) {
      console.log(`\n🎉 ${manualResult.result}`);
    }

  } catch (error) {
    console.error('❌ Local AI call failed:', error.message);
    
    // 失败时使用手动方案
    console.log('\n🔄 Switching to reliable manual execution...');
    const manualResult = await manualExecution();
    
    if (manualResult.success) {
      console.log(`\n🎉 ${manualResult.result}`);
    }
  }
}

// 执行主函数
main().catch(console.error);