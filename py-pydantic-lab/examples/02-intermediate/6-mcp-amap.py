"""
示例 6: 高德地图 MCP 集成 (Location Intelligence)

核心价值：将 Agent 连接到地理位置服务，实现天气查询、路线规划、地理编码等功能。
功能集成 (@amap/amap-maps-mcp-server)：
1. get_weather: 获取指定城市的实时天气或预报。
2. get_geocode: 将地址转换为经纬度坐标。
3. get_regeocode: 将经纬度转换为详细地址。
4. walking_route / driving_route: 规划步行或驾车路线。

架构说明：
1. 使用 Pydantic AI 的 MCPServerStdio 连接到高德地图 MCP 服务器。
2. 演示 Agent 如何利用 LBS 能力解决现实生活中的出行与环境查询问题。
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
    load_dotenv()

# 将 examples 目录添加到 sys.path 以允许从 common 导入
examples_root = Path(__file__).resolve().parents[1]
if str(examples_root) not in sys.path:
    sys.path.append(str(examples_root))

from common.models import get_model

async def main():
    print('--- 示例 6: 高德地图 MCP 集成 (地理位置智能) ---')
    
    # 1. 检查必要配置
    api_key = os.getenv('AMAP_MAPS_API_KEY')
    if not api_key:
        print("\n[跳过运行] 提示：未检测到 AMAP_MAPS_API_KEY。")
        print("请在 .env 中配置高德地图 API Key 以实际运行此示例。")
        print("您可以从 https://lbs.amap.com/ 免费申请。")
        return

    # 2. 定义 MCP 服务器配置
    # 使用 npx 运行 @amap/amap-maps-mcp-server
    server = MCPServerStdio(
        'npx',
        args=['-y', '@amap/amap-maps-mcp-server'],
        env={**os.environ, "AMAP_MAPS_API_KEY": api_key}
    )
    
    # 3. 初始化 Agent
    agent = Agent(
        get_model(),
        toolsets=[server],
        system_prompt=(
            "你是一个专业的‘出行管家’和‘地理位置专家’。"
            "你可以利用高德地图提供的工具来回答关于地点、天气、路线和地理编码的问题。"
            "\n你的职责包括：\n"
            "1. 为用户提供准确的天气信息及穿衣/出行建议。\n"
            "2. 规划最优路线（步行或驾车），并解释路线经过的关键点。\n"
            "3. 帮助用户定位具体地址或坐标。\n"
            "请以友好且实用的语气进行回复，如果涉及到路线规划，请尽量详细描述每一步。"
        )
    )
    
    # 4. 运行示例
    async with server:
        # 示例查询：天气 + 路线规划
        prompt = "帮我查一下上海明天的天气，并规划一条从‘外滩’到‘静安寺’的步行路线。"
        print(f"\nPrompt: {prompt}")
        print("正在连接高德地图 MCP 并处理您的请求，请稍候...\n")
        
        try:
            result = await agent.run(prompt)
            print("\n=== AI 助手回复 ===")
            print(result.output)
            print("\n====================")
        except Exception as e:
            print(f"\n调用失败: {e}")
            print("提示：请检查您的高德 API Key 是否有效，以及网络连接是否正常。")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"程序异常: {e}")
