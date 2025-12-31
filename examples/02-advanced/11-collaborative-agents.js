/**
 * 示例 11: 多模型协作 (Collaborative Agents / Multi-model Workflow)
 * 
 * 核心价值：解耦任务与模型 (Decoupling Tasks from Models)
 * Vercel AI SDK 允许你轻松地将不同模型的输出作为另一个模型的输入。
 * 这种“流水线”模式比让一个模型处理所有事情更可靠、更专业。
 */

const { generateText } = require('ai');
const { ollama } = require('ai-sdk-ollama');

async function main() {
  console.log('--- 示例 11: 多模型协作流水线 ---\n');

  // 定义两个不同的角色（甚至可以使用不同的模型）
  const writerModel = ollama('qwen2.5-coder:latest');
  const reviewerModel = ollama('phi4:latest');

  // 第一步：Writer 生成初稿
  console.log('1. [Writer] 正在生成技术说明初稿...');
  const { text: draft } = await generateText({
    model: writerModel,
    system: '你是一位资深后端工程师，擅长简洁明了地解释技术概念。',
    prompt: '请用 100 字以内解释什么是 Redis 的持久化。',
  });

  console.log(`\n--- 初稿 ---\n${draft}\n`);

  // 第二步：Reviewer 进行审查并提出建议
  console.log('2. [Reviewer] 正在审查初稿并提供改进建议...');
  const { text: review } = await generateText({
    model: reviewerModel,
    system: '你是一位严苛的技术编辑，负责确保内容的准确性和专业性。',
    prompt: `请审查以下关于 Redis 持久化的说明，并给出 2 条具体的改进建议：\n\n${draft}`,
  });

  console.log(`\n--- 审查建议 ---\n${review}\n`);

  // 第三步：Writer 根据建议进行最终修改
  console.log('3. [Writer] 正在根据建议进行最终润色...');
  const { text: finalVersion } = await generateText({
    model: writerModel,
    system: '你是一位擅长吸收反馈的资深工程师。',
    prompt: `请参考以下建议，对初稿进行最终润色：\n\n建议：${review}\n\n初稿：${draft}`,
  });

  console.log(`\n--- 最终版本 ---\n${finalVersion}\n`);
}

main().catch(console.error);
