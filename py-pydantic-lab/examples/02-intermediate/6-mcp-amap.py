"""
示例 6: 高德地图 (AMap) MCP 集成

核心价值：将 Agent 连接到地理信息服务（LBS），实现位置搜索、周边查询、路线规划等功能。
功能集成 (@amap/amap-maps-mcp-server)：
1. search_poi: 搜索周边兴趣点（POI）。
2. get_weather: 获取指定地区的实时天气。
3. get_geocode: 将地址转换为经纬度。
4. get_distance: 计算两点间的距离。

架构说明：
1. 使用 Pydantic AI 的 MCPServerStdio 连接到 @amap/amap-maps-mcp-server。
2. 展示如何通过 MCP 协议将第三方 API 能力无缝注入到 Agent 的工具箱中。
3. 演示“需求理解 -> 地理搜索 -> 信息整合”的 LBS 应用工作流。
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

# 加载环境变量
# 尝试从多个可能的路径加载 .env 文件
env_paths = [
    Path(__file__).resolve().parent / ".env",           # 当前目录
    Path(__file__).resolve().parents[2] / ".env",       # py-pydantic-lab 目录
    Path(__file__).resolve().parents[3] / ".env",       # 项目根目录
]

loaded = False
for env_path in env_paths:
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        print(f"已从 {env_path} 加载环境变量")
        loaded = True
        break

if not loaded:
    # 如果都没找到，尝试默认加载
    load_dotenv()

# 将 examples 目录添加到 sys.path 以允许从 common 导入
examples_root = Path(__file__).resolve().parents[1]
if str(examples_root) not in sys.path:
    sys.path.append(str(examples_root))

from common.models import get_model

async def main():
    print('--- 示例 6: 高德地图 MCP 集成 (LBS 智能助手) ---')
    
    # 1. 检查必要配置
    # amap-maps 需要 AMAP_MAPS_API_KEY
    if not os.getenv('AMAP_MAPS_API_KEY'):
        print("\n[跳过运行] 提示：未检测到 AMAP_MAPS_API_KEY。")
        print("请在 .env 中配置高德地图 API Key 以实际运行此示例。")
        print("您可以从 https://lbs.amap.com/ 获取 Key。")
        # 如果没有 key，我们仅展示代码逻辑
        return

    # 2. 定义 MCP 服务器配置
    # 使用 npx 运行 @amap/amap-maps-mcp-server
    # 对应用户提供的配置：
    # "amap-maps": { 
    #   "args": ["-y", "@amap/amap-maps-mcp-server"], 
    #   "command": "npx", 
    #   "env": { "AMAP_MAPS_API_KEY": "..." } 
    # }
    server = MCPServerStdio(
        'npx',
        args=['-y', '@amap/amap-maps-mcp-server'],
        env=os.environ.copy(),
        timeout=30  # 增加初始化超时时间
    )
    
    # 3. 初始化 Agent
    agent = Agent(
        get_model(),
        toolsets=[server],
        system_prompt=(
            "你是一个极其聪明的地理信息专家和出行规划助手。"
            "你能熟练运用高德地图提供的各种工具（搜索 POI、查天气、算距离等）来解决用户的问题。"
            "\n你的目标是：\n"
            "1. **精准定位**：准确理解用户想要去的地方或关注的区域。\n"
            "2. **多维分析**：结合天气、距离和周边设施，给出综合建议。\n"
            "3. **人性化交互**：以友好、专业的语气回复，并主动提供可能有用的补充信息。"
            "\n当用户提出关于地点、出行或天气的请求时，请调用相应的 MCP 工具。"
        )
    )
    
    # 4. 运行示例
    async with server:
        # 验证：列出从 MCP Server 获取到的工具
        print("\n[验证] 成功连接到 MCP Server。可用工具列表：")
        tools = await server.list_tools()
        for tool in tools:
            print(f" - {tool.name}: {tool.description[:60]}...")
        
        # 用户的查询请求
        prompt = "我想在杭州西湖附近找一家评价好的咖啡馆，顺便告诉我那里的天气怎么样？"
        print(f"\nPrompt: {prompt}")
        print("正在连接高德地图 MCP 进行实时搜索...\n")
        
        try:
            result = await agent.run(prompt)
            print("\n=== AI 助手回复 ===")
            print(result.output)
            print("\n====================")
        except Exception as e:
            print(f"\n[运行出错]: {e}")
            print("请确保已安装 Node.js 且 npx 命令可用。")

if __name__ == "__main__":
    asyncio.run(main())
