"""
示例 7: 历史天气 MCP 集成 (Time-Travel Weather Analysis)

核心价值：将 Agent 连接到全球历史气象数据，实现跨越时空的分析能力。
功能集成 (@dangahagan/weather-mcp):
1. get_historical_weather: 查询指定地点、指定日期的历史天气（支持 1940 年至今）。
2. forecast: 获取未来天气预报。
3. current_conditions: 获取实时天气状况。

架构说明：
1. 使用 Pydantic AI 的 MCPServerStdio 连接到基于 Open-Meteo 数据源的 MCP 服务器。
2. 展示 Agent 如何结合“时间”和“空间”两个维度，对过去发生的事件进行气象背景复盘。
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

# 将 examples 目录添加到 sys.path
examples_root = Path(__file__).resolve().parents[1]
if str(examples_root) not in sys.path:
    sys.path.append(str(examples_root))

from common.models import get_model

async def main():
    print('--- 示例 7: 历史天气 MCP 集成 (气象考古学家) ---')
    
    # 1. 定义 MCP 服务器配置
    # @dangahagan/weather-mcp 支持 1940 年至今的历史数据，通常不需要 API Key (Open-Meteo)
    server = MCPServerStdio(
        'npx',
        args=['-y', '@dangahagan/weather-mcp']
    )
    
    # 2. 初始化 Agent
    agent = Agent(
        get_model(),
        toolsets=[server],
        system_prompt=(
            "你是一个结合了‘气象专家’和‘历史分析师’身份的 Agent。"
            "你可以查询全球任何地点从 1940 年至今的精确历史天气数据。"
            "\n你的任务是：\n"
            "1. 根据用户提供的日期和地点，查询当时的温度、降水、风速等信息。\n"
            "2. 尝试从气象角度分析这些数据对当时可能产生的影响（例如：为什么那天适合/不适合做某事）。\n"
            "3. 保持专业、严谨且富有洞察力的语气。"
        )
    )
    
    # 3. 运行示例
    async with server:
        # 场景：查询一个具有历史意义的日子（例如：1969年7月20日阿波罗11号登月当天，佛罗里达州肯尼迪航天中心的天气）
        # 或者查询用户出生的那一天
        prompt = "1997年7月1日香港回归那天，香港的天气如何？请帮我查一下，并描述一下那天的气候特征。"
        print(f"\nPrompt: {prompt}")
        print("正在连接历史天气 MCP 穿越时空中，请稍候...\n")
        
        try:
            result = await agent.run(prompt)
            print("\n=== AI 助手回复 ===")
            print(result.output)
            print("\n====================")
        except Exception as e:
            print(f"\n调用失败: {e}")
            print("提示：该 MCP 依赖网络访问 Open-Meteo API，请确保网络连接正常。")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"程序异常: {e}")
