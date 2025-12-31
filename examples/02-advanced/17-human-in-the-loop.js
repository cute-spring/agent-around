/**
 * 示例 17: 人工介入 (Human-in-the-loop, HITL)
 * 
 * 核心原理：
 * 在 Agent 自动化流程中，对于某些“高风险”操作（如删除文件、发送邮件、执行转账等），
 * 我们不希望 Agent 完全自主执行。通过在工具的 `execute` 函数中加入拦截逻辑，
 * 强制要求人类用户在控制台进行二次确认，从而实现安全治理。
 */
const { generateText, tool } = require('ai');
const { ollama } = require('ai-sdk-ollama');
const readline = require('readline');
require('dotenv').config();

/**
 * 终端交互助手：获取用户命令行输入以进行确认
 */
function askConfirmation(question) {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  return new Promise((resolve) => {
    rl.question(`\n⚠️  [安全拦截] ${question} (y/n): `, (answer) => {
      rl.close();
      resolve(answer.toLowerCase() === 'y');
    });
  });
}

async function main() {
  console.log('--- 人工介入 (HITL) 模式演示 ---');
  console.log('Agent 在执行敏感操作前会请求您的许可。\n');

  const result = await generateText({
    model: ollama('qwen2.5-coder:latest'),
    maxSteps: 5,
    system: '你是一个具备文件管理能力的助手。如果用户要求删除文件，请务必调用 deleteFile 工具。',
    prompt: '请帮我删除系统中的临时数据文件 "temp_data.csv"。',
    tools: {
      deleteFile: tool({
        description: '从系统中删除指定文件。此操作不可逆，需谨慎使用。',
        parameters: require('zod').object({
          filename: require('zod').string().describe('要删除的文件名'),
        }),
        execute: async ({ filename }) => {
          // --- 核心拦截逻辑 ---
          // 在真正执行删除逻辑前，调用交互函数请求人工授权
          const confirmed = await askConfirmation(`您确定要删除文件 "${filename}" 吗？`);
          
          if (!confirmed) {
            console.log(`[工具执行] 用户拒绝了操作，取消删除。`);
            return `操作已由人类用户取消。文件 "${filename}" 未被删除。`;
          }

          // 模拟实际的删除操作
          console.log(`[工具执行] 正在执行删除操作: ${filename}...`);
          return `成功删除了文件 "${filename}"。`;
        },
      }),
    },
  });

  // 如果模型返回了类似 JSON 的工具调用但没有真正触发 execute (常见于小型本地模型)
  if (result.toolCalls.length === 0 && result.text.includes('"name": "deleteFile"')) {
    console.log('\n[提示] 检测到模型输出了工具调用格式但未自动执行，正在手动触发拦截演示...');
    const confirmed = await askConfirmation(`您确定要删除文件 "temp_data.csv" 吗？`);
    if (confirmed) {
      console.log(`[工具执行] 正在执行删除操作: temp_data.csv...`);
      console.log(`\nFinal Response (Agent 最终回复): 成功删除了文件 "temp_data.csv"。`);
    } else {
      console.log(`[工具执行] 用户拒绝了操作，取消删除。`);
      console.log(`\nFinal Response (Agent 最终回复): 操作已由人类用户取消。文件 "temp_data.csv" 未被删除。`);
    }
    return;
  }

  console.log('\nFinal Response (Agent 最终回复):');
  console.log(result.text);
}

main().catch(console.error);
