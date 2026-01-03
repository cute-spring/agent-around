"""
示例 4: 工具调用 (Tool Calling)

核心价值：Agent 的能力扩展
通过 @agent.tool 装饰器，你可以轻松地为 Agent 注入外部能力（如调用 API、执行数据库查询等）。
PydanticAI 会自动将函数签名转换为 LLM 可理解的 JSON Schema。
"""

import sys
import random
from pathlib import Path
from pydantic_ai import Agent, RunContext

# 将 examples 目录添加到 sys.path 以允许从 common 导入
examples_root = Path(__file__).resolve().parents[1]
if str(examples_root) not in sys.path:
    sys.path.append(str(examples_root))

from common.models import get_model
from typing import Literal, Optional
from pydantic_ai import Agent, RunContext

# 1. 初始化 Agent
agent = Agent(
    get_model(),
    system_prompt="You are a helpful assistant that can check the weather and roll dice."
)

# 2. 定义工具
@agent.tool
def get_weather(
    ctx: RunContext[None], 
    location: str, 
    date: str = 'today',
    unit: Literal['celsius', 'fahrenheit'] = 'celsius'
) -> str:
    """
    Get the weather forecast for a given location at a specific date.
    
    Args:
        location: The city and country, e.g. 'London, UK'.
        date: The date for the forecast, e.g. 'tomorrow' or '2024-01-01'.
        unit: The temperature unit to use.
    """
    temp = 25 if unit == 'celsius' else 77
    symbol = "°C" if unit == 'celsius' else "°F"
    return f"The weather in {location} on {date} is sunny and {temp}{symbol}."

@agent.tool
def roll_die(ctx: RunContext[None]) -> int:
    """Roll a 6-sided die."""
    return random.randint(1, 6)

def main():
    # 【架构师笔记：工具调用的深度思考】
    # 1. 语义化驱动：写好工具的定义（名字、参数、注释）其实就是在给 Agent 编写“使用说明书”。
    # 2. 强类型约束：使用 typing.Literal 和类型提示，能有效防止 LLM 生成错误的参数（如不存在的单位）。
    # 3. 链式推理 (Chaining)：Agent 能够根据第一个工具的结果，自主决定是否调用第二个工具，并综合给出建议。
    # 4. 自动提取：LLM 能够从自然语言（如 "tomorrow", "Fahrenheit"）中精准提取并转换成函数参数。
    print('--- 示例 4: 工具调用 ---')
    
    # 场景 1: 查询天气 (带复杂参数)
    prompt1 = "What will be the weather in New York tomorrow in Fahrenheit?"
    print(f"\nPrompt 1: {prompt1}")
    result1 = agent.run_sync(prompt1)
    print(f"Response: {result1.output}")

    # 场景 2: 多个工具调用或多轮推理
    prompt2 = "Check the weather in Tokyo for next Monday, and then roll a die to decide if I should go out."
    print(f"\nPrompt 2: {prompt2}")
    result2 = agent.run_sync(prompt2)
    print(f"Response: {result2.output}")

if __name__ == '__main__':
    main()
