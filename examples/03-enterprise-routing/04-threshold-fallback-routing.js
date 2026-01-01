/**
 * 方案 4: 置信度阈值与兜底路由 (Confidence Threshold & Fallback)
 * 
 * 【原因】
 * AI 并不总是可靠的。如果路由器的置信度过低，盲目自动分发会导致糟糕的用户体验（如技术问题被转接到财务）。
 * 
 * 【目标】
 * 引入量化的“置信度阈值”，将路由结果分为三类：自动执行、人工介入、拒绝/澄清。
 * 
 * 【结果】
 * 1. 明确区分了“确定的意图”和“模糊的噪音”。
 * 2. 保证了在 AI 不确定时，系统能优雅地转接到人工或请求用户补充信息。
 * 
 * 【可进一步提升的地方】
 * 1. 动态阈值调整：根据部门负荷自动调整阈值。如果人工客服繁忙，则提高阈值让 AI 处理更多；如果空闲，则降低阈值让更多任务进入人工审核以保证质量。
 * 2. 引入多重验证：同时调用两个不同模型（如 GPT-4o 和 Claude），如果结果不一致，则自动触发人工复核。
 */
const { cosineSimilarity, getEmbedding } = require('./utils');
require('dotenv').config();

// 设定目标部门的语义特征
const TARGET_SEMANTICS = {
  REFUND: '我想要退还我的钱，我不满意服务，申请退款流程'
};

async function routeWithThreshold(input) {
  const PASS_THRESHOLD = 0.8;    // 直接通过
  const REVIEW_THRESHOLD = 0.6;  // 需要人工复核
  
  console.log(`\n--- 处理输入: "${input}" ---`);
  
  const inputVec = await getEmbedding(input);
  const targetVec = await getEmbedding(TARGET_SEMANTICS.REFUND);
  const score = cosineSimilarity(inputVec, targetVec);
  
  console.log(`[系统] 语义匹配得分: ${score.toFixed(4)}`);

  if (score >= PASS_THRESHOLD) {
    console.log(`✅ [状态: 自动分发] 得分达标，直接路由至退款部门。`);
  } else if (score >= REVIEW_THRESHOLD) {
    console.log(`⚠️  [状态: 人工复核] 意图不明确，正在转接至人工预审...`);
  } else {
    console.log(`❌ [状态: 拒绝/兜底] 无法识别意图，路由至通用帮助中心。`);
  }
}

async function main() {
  console.log('--- 企业级方案 4: 阈值与三级动作策略 ---');
  await routeWithThreshold('我不想要了，把钱退给我');
  await routeWithThreshold('这个产品的颜色我觉得还可以改进');
  await routeWithThreshold('今天天气不错');
}

main().catch(console.error);
