"""
示例 9: OpenWeatherMap MCP 集成 (行业标准天气服务)

核心价值：接入全球最流行的天气数据提供商，提供实时、预测、空气质量及地理编码等全方位服务。

功能集成 (mcp-openweathermap):
1. get-current-weather: 获取指定城市的实时天气状况。
2. get-weather-forecast: 获取 5 天/3 小时预报。
3. get-air-pollution: 获取空气质量数据。
4. geocode-location: 地理编码（地名转坐标）。

架构说明：
1. 使用 Pydantic AI 的 MCPServerStdio 连接到 OpenWeatherMap MCP 服务器。
2. 展示了如何通过环境变量安全地传递 API Key 给 MCP 服务器。
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

# 加载环境变量
env_paths = [
    Path(__file__).resolve().parent / ".env",
    Path(__file__).resolve().parents[2] / ".env",
    Path(__file__).resolve().parents[3] / ".env",
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

# 获取 API Key
api_key = os.getenv("OPENWEATHER_API_KEY")

# 将 examples 目录添加到 sys.path
examples_root = Path(__file__).resolve().parents[1]
if str(examples_root) not in sys.path:
    sys.path.append(str(examples_root))

from common.models import get_model

async def main():
    print('--- 示例 9: OpenWeatherMap MCP 集成 (行业标准) ---')
    
    if not api_key:
        print("\n⚠️ 错误：未配置 OPENWEATHER_API_KEY。")
        print("请访问 https://openweathermap.org/api 注册免费 Key (通常选择 Free plan 即可)。")
        print("然后将其填入 .env 文件中的 OPENWEATHER_API_KEY 字段。")
        return

    # 1. 定义 MCP 服务器配置
    # 注意：这里我们通过 env 参数将 API Key 传递给 MCP 服务器
    server = MCPServerStdio(
        'npx',
        args=['-y', 'mcp-openweathermap'],
        env={**os.environ, "OPENWEATHER_API_KEY": api_key}
    )
    
    # 2. 初始化 Agent
    agent = Agent(
        get_model(),
        toolsets=[server],
        system_prompt=(
            "你是一个气象助手。你可以使用 OpenWeatherMap 提供的数据来回答关于天气、预测、空气质量和地理位置的问题。"
            "如果用户询问多个城市，你可以并行查询。"
            "请提供通俗易懂的解释，并在必要时给出建议（如：是否需要带伞、是否适合户外运动）。"
        )
    )
    
    # 3. 运行示例
    async with server:
        prompt = "查一下北京和上海现在的天气和空气质量，并对比一下两地的体感差异。"
        print(f"\nPrompt: {prompt}")
        print("正在连接 OpenWeatherMap MCP 获取最新数据...\n")
        
        try:
            result = await agent.run(prompt)
            print("\n=== AI 助手回复 ===")
            print(result.output)
            print("\n====================")
        except Exception as e:
            print(f"\n调用失败: {e}")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"程序异常: {e}")
