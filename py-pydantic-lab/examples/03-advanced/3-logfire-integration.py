"""
示例 03-advanced/3-logfire-integration.py: Logfire 监控集成 (Logfire Integration)

核心价值：看透 Agent 的“思考过程”
调试 Agent 最痛苦的是不知道它内部发生了几次重试、调用了什么工具。
Logfire 是 Pydantic 官方提供的监控工具，与 PydanticAI 原生集成。
"""

import sys
import os
from pathlib import Path
from pydantic_ai import Agent

# 将 examples 目录添加到 sys.path
examples_root = Path(__file__).resolve().parents[1]
if str(examples_root) not in sys.path:
    sys.path.append(str(examples_root))

from common.models import get_model

# 1. 配置 Logfire
# 在实际项目中，你需要运行 `logfire auth` 并在代码中配置
# 这里我们演示其基本集成逻辑
try:
    import logfire
    # 简单的控制台输出模式，不发送到服务器
    logfire.configure(send_to_logfire=False) 
    print("✅ Logfire 已配置 (当前为控制台静默模式)")
except ImportError:
    print("⚠️ 未安装 logfire，请运行: pip install logfire")
    logfire = None

# 2. 初始化 Agent 并启用仪器化 (Instrumentation)
agent = Agent(
    get_model(),
    system_prompt="你是一个幽默的科学老师。"
)

# 如果 logfire 可用，PydanticAI 会自动捕捉所有的工具调用和模型交互
if logfire:
    logfire.instrument_pydantic() # 监控 Pydantic 模型
    # PydanticAI 的调用会自动被 logfire 的上下文捕获

async def main():
    print('--- 示例: Logfire 监控集成 ---')
    
    # 在 logfire 的跨度(span)中运行，可以看到完整的追踪树
    if logfire:
        with logfire.span("Running Science Agent Task"):
            result = await agent.run("解释一下为什么天空是蓝色的？")
            print(f"Agent: {result.output}")
    else:
        result = await agent.run("解释一下为什么天空是蓝色的？")
        print(f"Agent: {result.output}")

    # 【架构师笔记：可观测性 (Observability)】
    # 1. 追踪树：在 Logfire 仪表盘中，你可以看到嵌套的调用关系（Agent -> Tool -> Model -> Validator）。
    # 2. 性能瓶颈：一眼就能看出是哪个 API 调用慢，或者是哪个 Validator 耗时过长。
    # 3. 成本分析：Logfire 会记录每次请求的 Token 消耗，方便统计项目成本。

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
