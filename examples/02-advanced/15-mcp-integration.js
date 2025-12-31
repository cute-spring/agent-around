/**
 * 示例 15: MCP (Model Context Protocol) 集成
 * 
 * 核心价值：标准化插件生态 (Standardized Ecosystem)
 * MCP 是由 Anthropic 发起的协议，旨在让 AI 能够通过统一的标准连接各种工具。
 * 以前你需要为每个工具写适配器，现在只需接入一个 MCP Server。
 */

const { generateText } = require('ai');
const { ollama } = require('ai-sdk-ollama');
// 注意：在实际项目中需要安装 @modelcontextprotocol/sdk
// 这里作为概念展示 SDK v6 如何通过工具化思路接入 MCP 理念

async function main() {
  console.log('--- 示例 15: MCP 协议集成概念演示 ---');

  /**
   * 场景说明：
   * 假设我们有一个 MCP Server 提供了 "fetch_github_stars" 功能。
   * SDK v6 允许我们将 MCP 暴露出来的 tools 直接解构到 generateText 中。
   */

  const result = await generateText({
    model: ollama('qwen2.5-coder:latest'),
    prompt: '查询一下 vercel/ai 这个仓库在 GitHub 上有多少 star？',
    
    // 核心价值：MCP Tools
    // 在真实 MCP 环境中，你会使用 mcpClient.listTools() 获取这些定义
    tools: {
      github_search: {
        description: 'MCP 提供的 GitHub 搜索工具',
        parameters: {
          type: 'object',
          properties: {
            repo: { type: 'string', description: '仓库名' }
          }
        },
        execute: async ({ repo }) => {
          console.log(`\n[MCP Server 执行] 正在请求 GitHub API 查询 ${repo}...`);
          return { stars: 85400 }; // 模拟 MCP 返回结果
        }
      }
    },
    maxSteps: 3
  });

  console.log('\n--- 最终结果 ---');
  console.log(result.text);
  console.log('\n💡 提示：SDK v6 与 MCP 的结合让 AI 具备了无限的扩展能力，从读文件到控制智能家居。');
}

main().catch(console.error);
