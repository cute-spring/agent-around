/**
 * 示例 3: 结构化输出 (Structured Output)
 * 
 * 核心价值：强类型约束与自动解析 (Type Safety & Auto-parsing)
 * 仅仅让 AI 返回 JSON 是不够的，SDK 通过 zod 强制 AI 遵循你定义的 Schema。
 * 这让 AI 的输出可以直接被程序逻辑使用，而不会因为格式错误崩溃。
 */

const { generateObject } = require('ai');
const { ollama } = require('ai-sdk-ollama');
const { z } = require('zod');

async function main() {
  console.log('--- 示例 3: 强类型结构化输出 ---');

  // generateObject 确保 AI 返回的结果符合 zod 定义的模型
  const { object } = await generateObject({
    model: ollama('qwen2.5-coder:latest'),
    // 核心价值：定义输出的“形状”，SDK 会自动将其转化为 prompt 中的约束
    schema: z.object({
      recipe: z.object({
        name: z.string().describe('菜名'),
        ingredients: z.array(z.object({
          name: z.string().describe('食材名称'),
          amount: z.string().describe('用量'),
        })),
        steps: z.array(z.string()).describe('制作步骤'),
      }),
    }),
    prompt: '帮我生成一个巧克力饼干的简单食谱。',
  });

  // 这里的 object 已经经过了 zod 校验和解析，可以直接安全使用
  console.log('生成的结构化数据:');
  console.log(JSON.stringify(object, null, 2));
}

main().catch(console.error);
