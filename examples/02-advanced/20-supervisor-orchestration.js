/**
 * 示例 20: Supervisor Orchestration (中控路由/动态分发)
 * 
 * 核心原理：
 * 这是一个“中枢”模式。Supervisor Agent 不直接完成具体任务，而是充当调度员。
 * 它分析用户的需求，决定调用哪一个专门的 Worker Agent。
 * 
 * 优势：
 * 1. 专注性：Worker Agent 只需要处理特定领域的任务。
 * 2. 扩展性：增加新功能只需增加新的 Worker 和 Supervisor 的路由逻辑。
 */
const { generateText } = require('ai');
const { ollama } = require('ai-sdk-ollama');
require('dotenv').config();

const model = ollama('qwen2.5-coder:latest');

/**
 * 专门负责“研究”的 Worker
 */
async function researcherAgent(topic) {
  console.log(`[Researcher] 正在深入研究话题: ${topic}...`);
  const { text } = await generateText({
    model,
    system: '你是一位专业的研究员。请提供关于给定话题的 3 个核心事实。',
    prompt: topic,
  });
  return text;
}

/**
 * 专门负责“文案”的 Worker
 */
async function writerAgent(content) {
  console.log(`[Writer] 正在润色文案内容...`);
  const { text } = await generateText({
    model,
    system: '你是一位资深编辑。请将以下事实改写成一段生动的、适合在社交媒体发布的文字。',
    prompt: content,
  });
  return text;
}

/**
 * Supervisor Agent: 负责分析需求并调度
 */
async function supervisor(userInput) {
  console.log(`\n--- Supervisor 收到请求: "${userInput}" ---`);

  // 1. 意图分析：判断需要哪个 Worker
  const { text: intent } = await generateText({
    model,
    system: `你是一位项目经理。分析用户的输入，只输出一个单词：
    - 如果用户想了解信息、查事实，输出 "RESEARCH"。
    - 如果用户想写文章、润色、创作，输出 "WRITE"。
    - 其他情况，输出 "UNKNOWN"。`,
    prompt: userInput,
  });

  const cleanedIntent = intent.trim().toUpperCase();
  console.log(`[Supervisor] 识别到任务意图: ${cleanedIntent}`);

  // 2. 动态分发
  if (cleanedIntent.includes('RESEARCH')) {
    const researchResult = await researcherAgent(userInput);
    console.log(`\n[Researcher 结果]:\n${researchResult}`);
    
    // 级联：研究完后，询问用户是否需要润色
    console.log('\n[Supervisor] 研究完成。通常下一步我们可以交给 Writer 润色。');
    const finalPost = await writerAgent(researchResult);
    console.log(`\n[Writer 最终产出]:\n${finalPost}`);
  } 
  else if (cleanedIntent.includes('WRITE')) {
    const draft = await writerAgent(userInput);
    console.log(`\n[Writer 结果]:\n${draft}`);
  } 
  else {
    console.log('[Supervisor] 抱歉，我无法确定如何分配这个任务。');
  }
}

async function main() {
  console.log('--- Supervisor Orchestration 模式演示 ---');
  
  // 场景 A: 知识搜索 + 自动润色
  await supervisor('帮我查一下什么是 OpenCode，并整理成推文。');

  // 场景 B: 直接创作
  // await supervisor('写一段关于上海深夜食堂的感性文字。');
}

main().catch(console.error);
