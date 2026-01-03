"""
示例 2: 流式传输 (Streaming)

核心价值：极简的流式响应处理
在传统的开发中，处理 LLM 的流式输出（SSE）非常复杂。
PydanticAI 通过异步上下文管理器，让你可以像处理普通循环一样处理流。
"""

import sys
import asyncio
from pathlib import Path
from pydantic_ai import Agent

# 将 examples 目录添加到 sys.path 以允许从 common 导入
examples_root = Path(__file__).resolve().parents[1]
if str(examples_root) not in sys.path:
    sys.path.append(str(examples_root))

from common.models import get_model

# 初始化 Agent
agent = Agent(get_model())

async def main():
    print('--- 示例 2: 极简流式输出 ---')
    
    prompt = '请写一首关于人工智能的短诗。'
    print(f"Prompt: {prompt}\n")
    print("正在接收流式回复:")

    # 使用 run_stream 进行流式调用
    async with agent.run_stream(prompt) as result:
        # 【架构师笔记：流式输出的两种模式】
        # 问题现象：如果直接使用 result.stream_text()，输出会出现“复读机”现象（如 A, AB, ABC...）。
        # 原因：PydanticAI 的 stream_text() 默认是“累积模式”(Cumulative)，每次迭代返回自开始以来的全部文本。
        # 解决方案：设置 delta=True 切换到“增量模式”(Delta)，仅获取当前时刻新产生的文本片段。
        # 适用场景：
        #   - delta=True: 适用于终端实时打印、前端打字机效果。
        #   - delta=False (默认): 适用于需要不断获取最新完整回复进行状态更新的场景。
        async for message in result.stream_text(delta=True):
            print(message, end='', flush=True)
    
    print('\n\n生成完毕！')

if __name__ == '__main__':
    asyncio.run(main())
