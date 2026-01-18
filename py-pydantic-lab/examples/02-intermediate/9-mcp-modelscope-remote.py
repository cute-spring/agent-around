"""
示例 9: ModelScope 托管的 Remote MCP (Streamable HTTP)

核心价值：使用 ModelScope 提供的远程高德地图 MCP 服务，演示真实的 Remote 连接与鉴权。
关键配置：
- 类型: streamable_http
- URL: https://mcp.api-inference.modelscope.net/fe171450402749/mcp
- 鉴权: Bearer Token
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStreamableHTTP

# 1. 环境准备
env_paths = [
    Path(__file__).resolve().parent / ".env",           # 当前目录
    Path(__file__).resolve().parents[2] / ".env",       # py-pydantic-lab 目录
    Path(__file__).resolve().parents[3] / ".env",       # 项目根目录
]
for env_path in env_paths:
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        break

# 2. 从环境变量中提取配置
MODELSCOPE_URL = os.getenv("MODELSCOPE_MCP_URL")
MODELSCOPE_TOKEN = os.getenv("MODELSCOPE_MCP_TOKEN")

async def main():
    print('--- 示例 9: ModelScope Remote MCP (高德地图) ---')
    
    # 检查必要配置
    if not MODELSCOPE_URL or not MODELSCOPE_TOKEN:
        print("\n[错误] 请在 .env 文件中配置 MODELSCOPE_MCP_URL 和 MODELSCOPE_MCP_TOKEN")
        return

    # 3. 构造 Remote 连接
    # 使用 MCPServerStreamableHTTP 对应配置中的 "streamable_http"
    server = MCPServerStreamableHTTP(
        url=MODELSCOPE_URL,
        headers={
            "Authorization": f"Bearer {MODELSCOPE_TOKEN}"
        }
    )
    
    # 获取通用模型配置
    try:
        examples_root = Path(__file__).resolve().parents[1]
        if str(examples_root) not in sys.path:
            sys.path.append(str(examples_root))
        from common.models import get_model
        model = get_model()
    except ImportError:
        model = "openai:gpt-4o"

    # 4. 初始化 Agent
    agent = Agent(
        model,
        toolsets=[server],
        system_prompt=(
            "你是一个地理信息专家。"
            "你连接到了 ModelScope 托管的高德地图 MCP 服务。"
            "你可以帮助用户查询地点、天气、路径规划等实时信息。"
        )
    )
    
    # 5. 运行与验证
    async with server:
        print(f"\n[连接中] 目标: {MODELSCOPE_URL}")
        try:
            # 验证：获取远程工具列表
            tools = await server.list_tools()
            print(f"[成功] 已连接！发现 {len(tools)} 个远程工具:")
            for t in tools:
                print(f" - {t.name}: {t.description[:50]}...")
            
            # 执行一个实际查询
            prompt = "帮我查一下现在北京的天气，并推荐一个在奥林匹克公园附近的咖啡馆。"
            print(f"\nPrompt: {prompt}")
            
            result = await agent.run(prompt)
            print("\n=== AI 助手回复 ===")
            print(result.output)
            print("\n====================")
            
        except Exception as e:
            print(f"\n[运行失败] 请检查 Token 是否有效或网络连接。")
            print(f"错误详情: {e}")
            print("\n教练建议：")
            print("1. 检查 Authorization Header 格式是否正确。")
            print("2. 确认该 URL 是否在有效期内（Hosted MCP 链接通常有有效期）。")

if __name__ == "__main__":
    asyncio.run(main())
