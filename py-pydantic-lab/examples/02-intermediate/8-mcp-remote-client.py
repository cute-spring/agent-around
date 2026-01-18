"""
示例 8: Remote MCP 服务集成 (托管模式)

核心价值：演示如何连接到远程托管的 MCP 服务（如 Hosted MCP），而非本地子进程。
关键特性：
1. 使用 MCPServerSSE 连接到远程 URL。
2. 演示 AP_APP_ID 和 AP_APP_KEY 的鉴权逻辑。
3. 强调敏感信息（Remote URL, API Key）的保护。

注意：由于这是一个演示，我们使用模拟的 URL 和 Key。
在实际场景中，您需要从服务商处获取真实的连接信息。
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerSSE

# 1. 加载环境变量
# 在实际生产中，这些变量应该在 .env 文件或 CI/CD 环境中设置
env_paths = [
    Path(__file__).resolve().parent / ".env",
    Path(__file__).resolve().parents[2] / ".env",
]

for env_path in env_paths:
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        break

# 2. 配置 Remote MCP 参数
# 这里的 AP_APP_ID 和 AP_APP_KEY 是用户提到的敏感鉴权信息
REMOTE_MCP_URL = os.getenv("REMOTE_MCP_URL", "https://api.example-mcp.com/v1/sse")
AP_APP_ID = os.getenv("AP_APP_ID", "your-app-id")
AP_APP_KEY = os.getenv("AP_APP_KEY", "your-app-key")

async def main():
    print('--- 示例 8: Remote MCP 服务集成 (架构演示) ---')
    
    # 3. 构造鉴权头 (Authentication Headers)
    # 不同的 Hosted MCP 服务可能有不同的 Header 格式，这里演示常见的 ID/KEY 模式
    headers = {
        "X-App-Id": AP_APP_ID,
        "Authorization": f"Bearer {AP_APP_KEY}",
        "Content-Type": "application/json"
    }

    print(f"正在尝试连接远程 MCP 服务: {REMOTE_MCP_URL}")
    print(f"使用鉴权 ID: {AP_APP_ID}")
    
    # 4. 初始化 Remote MCP 服务器连接
    # MCPServerSSE 用于连接基于 SSE (Server-Sent Events) 的远程 MCP 服务器
    server = MCPServerSSE(
        url=REMOTE_MCP_URL,
        headers=headers
    )
    
    # 5. 初始化 Agent
    # 将远程服务器注入到 toolsets 中
    agent = Agent(
        "openai:gpt-4o",  # 这里假设使用 openai 模型，实际可根据 common.models 获取
        toolsets=[server],
        system_prompt=(
            "你是一个连接了远程专家工具集的智能助手。"
            "你可以调用远程服务器提供的搜索、数据分析或专业领域工具。"
            "当用户提出请求时，请优先检查远程工具集是否能提供帮助。"
        )
    )
    
    # 6. 模拟运行 (由于 URL 是模拟的，实际运行会捕获连接错误)
    print("\n[注意] 这是一个架构演示。如果没有真实的远程服务器，连接将会失败。")
    
    try:
        async with server:
            # 在连接成功后，我们可以列出远程工具
            print("\n[验证] 成功连接到远程 MCP Server。")
            tools = await server.list_tools()
            print(f"可用远程工具数量: {len(tools)}")
            for tool in tools:
                print(f" - {tool.name}: {tool.description[:60]}...")

            prompt = "请使用远程搜索工具帮我查一下 2026 年最新的 AI 设计模式趋势。"
            print(f"\nPrompt: {prompt}")
            
            result = await agent.run(prompt)
            print("\n=== AI 助手回复 ===")
            print(result.output)
            
    except Exception as e:
        print(f"\n[连接详情]: 由于这是模拟示例，无法连接到 {REMOTE_MCP_URL}")
        print(f"[错误信息]: {e}")
        print("\n--- 教练点评 ---")
        print("在 Stdio 模式下，你通常会看到 'npx' 启动日志；")
        print("而在 Remote 模式下，关键在于 HTTPS 连接和 Headers 中的 AP_APP_KEY。")
        print("请确保你的 .env 文件中配置了正确的 REMOTE_MCP_URL。")

if __name__ == "__main__":
    # 导入通用模型获取函数（如果可用）
    try:
        examples_root = Path(__file__).resolve().parents[1]
        if str(examples_root) not in sys.path:
            sys.path.append(str(examples_root))
        from common.models import get_model
    except ImportError:
        pass

    asyncio.run(main())
