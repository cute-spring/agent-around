/**
 * 示例 21: Self-Reflection / Self-Correction (自我反思与修正)
 * 
 * 核心原理：
 * 即使是强大的 LLM 也会犯错。Self-Reflection 模式让 Agent 能够：
 * 1. 尝试解决问题 (Draft)
 * 2. 检查自己的结果 (Reflection/Feedback)
 * 3. 基于反馈重新生成 (Refinement)
 * 
 * 这种模式在生成代码或复杂逻辑时能显著提高成功率。
 */
const { generateText } = require('ai');
const { ollama } = require('ai-sdk-ollama');
require('dotenv').config();

const model = ollama('qwen2.5-coder:latest');

async function selfReflectionCodingAgent(task) {
  console.log(`\n任务: ${task}`);

  // 第一步：生成初稿 (Draft)
  console.log('\n--- 1. 生成初稿 ---');
  const { text: draft } = await generateText({
    model,
    system: '你是一位程序员。请只输出代码，不要有任何解释。',
    prompt: task,
  });
  console.log(draft);

  // 第二步：自我审查 (Reflection)
  console.log('\n--- 2. 自我反思与审查 ---');
  const { text: feedback } = await generateText({
    model,
    system: '你是一位高级测试工程师。请审查以下代码，寻找潜在的错误、性能问题或不符合最佳实践的地方。如果有错，请指出；如果完美，请回复 "PASS"。',
    prompt: `代码内容:\n${draft}`,
  });
  console.log(`反馈意见: ${feedback}`);

  if (feedback.trim().toUpperCase() === 'PASS') {
    console.log('\n[结论] 代码通过审查！');
    return draft;
  }

  // 第三步：基于反馈进行修正 (Refinement)
  console.log('\n--- 3. 修正代码 ---');
  const { text: refinedCode } = await generateText({
    model,
    system: '你是一位资深工程师。请根据测试反馈修正之前的代码。只输出修正后的代码，不要解释。',
    prompt: `初稿:\n${draft}\n\n反馈意见:\n${feedback}`,
  });
  console.log(refinedCode);

  console.log('\n[结论] 代码已根据反馈完成修正。');
  return refinedCode;
}

async function main() {
  console.log('--- Self-Reflection Coding Agent 演示 ---');
  
  const task = '写一个 JavaScript 函数，计算两个日期之间相差的天数。要求考虑边界情况。';
  await selfReflectionCodingAgent(task);
}

main().catch(console.error);
