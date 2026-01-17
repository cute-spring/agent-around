"""
示例 4: MCP 集成 (Upstash Context7)

核心价值：通过 Model Context Protocol (MCP) 扩展 Agent 的能力，使其能够访问实时文档和结构化知识。
架构说明：
1. 使用 Pydantic AI 的 MCPServerStdio 连接到外部 MCP 服务器。
2. 集成 @upstash/context7-mcp 获取最新的库文档。
3. 展示如何通过工具调用链实现“文档查询 -> 知识增强 -> 回答问题”。
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

# 加载环境变量
load_dotenv()

# 将 examples 目录添加到 sys.path 以允许从 common 导入
examples_root = Path(__file__).resolve().parents[1]
if str(examples_root) not in sys.path:
    sys.path.append(str(examples_root))

from common.models import get_model

async def main():
    print('--- 示例 4: MCP 集成 (Upstash Context7) ---')
    
    # 1. 定义 MCP 服务器配置
    # 注意：需要系统中安装了 Node.js (npx)
    # 如果有 Upstash Context7 API Key，可以在环境变量中设置 CONTEXT7_API_KEY
    # 更多信息请访问: https://context7.com/
    env = os.environ.copy()
    if 'CONTEXT7_API_KEY' in os.environ:
        # 某些 MCP 服务器可能需要特定的环境变量名，Context7 默认通过命令行参数或内部环境变量读取
        # 这里演示如何透传环境变量
        env['API_KEY'] = os.environ['CONTEXT7_API_KEY']

    # 使用 MCPServerStdio 通过标准输入输出与 npx 启动的 MCP 服务器通信
    server = MCPServerStdio(
        'npx',
        args=['-y', '@upstash/context7-mcp@latest'],
        env=env
    )
    
    # 2. 初始化 Agent 并绑定 MCP toolset
    # Pydantic AI 的 toolsets 参数允许直接传入 MCP 服务器实例
    agent = Agent(
        get_model(),
        toolsets=[server],
        system_prompt=(
            "你是一个精通现代 Web 技术的资深架构师。"
            "当你被问及特定库（如 Next.js, Tailwind, Pydantic AI, MCP 等）的用法时，"
            "请务必先使用 Context7 工具查询最新的官方文档。"
            "交互步骤：\n"
            "1. 首先使用 'resolve-library-id' 查找库的 ID（例如：'next.js' -> '/vercel/next.js'）。\n"
            "2. 然后使用 'query-docs' 根据 ID 和具体问题获取最新的文档片段。\n"
            "3. 基于获取到的文档回答用户问题，并注明参考了 Context7 的实时数据。"
        )
    )
    
    # 3. 使用 async with 管理 MCP 服务器生命周期
    # 这将自动启动子进程并在退出时关闭它
    async with server:
        prompt = "如何使用 Next.js 15 的 Middleware 处理重定向？"
        print(f"\nPrompt: {prompt}")
        print("正在连接 MCP 服务器并查询文档，请稍候...\n")
        
        # 运行 Agent
        # Pydantic AI 会自动发现 MCP 服务器提供的工具，并在需要时调用它们
        result = await agent.run(prompt)
        
        print("\n=== AI 最终回复 ===")
        print(result.output)
        print("\n====================")

if __name__ == '__main__':
    # 确保环境中有必要的模型配置
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\n运行失败: {e}")
        print("\n提示: 请确保已安装 Node.js 并配置了有效的 LLM API Key。")
