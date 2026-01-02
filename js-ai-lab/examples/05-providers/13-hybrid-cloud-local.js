/**
 * 示例 13: 混合云/地协作 (Hybrid Local & Cloud Workflow)
 * 
 * 核心价值：成本与隐私优化 (Cost & Privacy Optimization)
 * 重构说明：此文件已改为从 ../../lib/ai-providers 加载配置。
 */

const { generateText, generateObject } = require('ai');
const { z } = require('zod');
const { local, cloud } = require('../../lib/ai-providers');

async function main() {
  console.log('--- 示例 13: 混合云/地协作流水线 ---\n');

  if (!process.env.ZHIPU_API_KEY || process.env.ZHIPU_API_KEY.includes('your_zhipu')) {
    console.error('错误: 请先在 .env 文件中设置有效的 ZHIPU_API_KEY');
    return;
  }

  // --- 场景：产品发布工作流 ---

  // 第一步：[云端大模型] 负责创意写作
  console.log('1. [云端 - 智谱 AI] 正在撰写富有感染力的产品宣传文案...');
  const { text: adCopy } = await generateText({
    model: cloud.zhipu,
    prompt: '请为一款名为 "AI Recharge" 的智能咖啡机写一段 150 字左右的宣传文案。',
  });

  console.log(`\n--- 宣传文案 (由云端生成) ---\n${adCopy}\n`);

  // 第二步：[本地模型] 负责结构化提取
  console.log('2. [本地 - Ollama] 正在从文案中提取核心关键词和卖点...');
  const { object: data } = await generateObject({
    model: local.chat,
    schema: z.object({
      productName: z.string(),
      keySellingPoints: z.array(z.string()).describe('从文中提取 3 个核心卖点'),
      suggestedPrice: z.number().describe('根据文案语境建议一个人民币价格'),
    }),
    prompt: `请分析以下文案并提取信息：\n\n${adCopy}`,
  });

  console.log('--- 提取的结构化数据 (由本地生成) ---');
  console.log(JSON.stringify(data, null, 2));

  console.log('\n✅ 混合工作流完成！成功结合了云端模型的创意与本地模型的结构化处理能力。');
}

main().catch(console.error);
