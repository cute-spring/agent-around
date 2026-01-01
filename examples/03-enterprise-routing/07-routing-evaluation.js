/**
 * 方案 7: 自动化路由评估系统 (Automated Routing Benchmark)
 * 
 * 【原因】
 * AI 系统的迭代是持续的。如果没有一套量化的评估标准，开发者无法确定新的 Prompt 或新的模型是否真的提升了路由准确率，还是引入了新的偏差。
 * 
 * 【目标】
 * 建立一套标准化的基准测试集（Benchmark），量化评估不同路由器的准确率（Accuracy）和平均延迟（Latency）。
 * 
 * 【结果】
 * 1. 能够一键生成路由器的质量报告。
 * 2. 支持不同方案（如 Hybrid vs LLM）的性能横向对比。
 * 3. 能够识别出容易出错的“Hard Cases”，为后续的优化提供方向。
 * 
 * 【可进一步提升的地方】
 * 1. 引入交叉验证（Cross-validation）：自动从真实生产日志中抽取数据生成测试集。
 * 2. 自动化集成：将此评估脚本接入 Git Hook，如果准确率低于 95%，则禁止代码提交。
 */
const { trace } = require('./utils');

// 测试集：包含输入和预期的正确分类
const TEST_SET = [
  { input: "我想退款", expected: "BILLING" },
  { input: "软件无法启动，报 404", expected: "TECHNICAL" },
  { input: "批量购买有优惠吗", expected: "SALES" },
  { input: "发票还没收到", expected: "BILLING" },
  { input: "权限不足无法访问", expected: "TECHNICAL" },
  { input: "你们的产品多少钱", expected: "SALES" },
  { input: "今天天气不错", expected: "HUMAN_FALLBACK" } // 预期触发兜底
];

async function evaluate(routerName, routerFn) {
  console.log(`\n=== 正在评估路由器: ${routerName} ===`);
  let correct = 0;
  let totalTime = 0;

  for (const test of TEST_SET) {
    const { result, duration, success } = await trace(routerName, () => routerFn(test.input));
    
    const isCorrect = result === test.expected;
    if (isCorrect) correct++;
    totalTime += duration;

    console.log(`[测试] 输入: "${test.input}" | 预期: ${test.expected} | 实际: ${result} | ${isCorrect ? '✅' : '❌'} (${duration}ms)`);
  }

  console.log(`\n--- ${routerName} 评估结果 ---`);
  console.log(`准确率: ${(correct / TEST_SET.length * 100).toFixed(2)}% (${correct}/${TEST_SET.length})`);
  console.log(`平均耗时: ${(totalTime / TEST_SET.length).toFixed(2)}ms`);
}

async function main() {
  // 注意：为了演示，我们只评估混合路由。
  // 在实际工程中，你会对比 LLM 路由、语义路由等多个版本的表现。
  
  // 模拟一个简单的路由器函数包装
  const mockHybridRouter = async (input) => {
    // 逻辑简化自 01-hybrid-routing
    if (input.includes('退款') || input.includes('发票')) return 'BILLING';
    if (input.includes('启动') || input.includes('权限')) return 'TECHNICAL';
    if (input.includes('购买') || input.includes('多少钱')) return 'SALES';
    return 'HUMAN_FALLBACK';
  };

  await evaluate("HybridRouter_v1", mockHybridRouter);
}

main().catch(console.error);
