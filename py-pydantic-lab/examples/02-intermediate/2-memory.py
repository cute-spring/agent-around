"""
示例 02-intermediate/2-memory.py: 记忆与多轮对话 (Memory & Multi-turn Chat)

核心价值：跨请求保持上下文
LLM 本身是“无状态”的（Stateless）。要实现对话，我们必须手动维护历史记录。
PydanticAI 通过 message_history 参数，让你能够轻松管理 Agent 的记忆。
"""

import sys
import asyncio
from pathlib import Path
from pydantic_ai import Agent

# 将 examples 目录添加到 sys.path
examples_root = Path(__file__).resolve().parents[1]
if str(examples_root) not in sys.path:
    sys.path.append(str(examples_root))

from common.models import get_model

# 初始化 Agent
agent = Agent(
    get_model(),
    system_prompt="你是一个友好的助手。请记住用户的名字和偏好。"
)

async def main():
    print('--- 示例: 记忆与多轮对话 (Memory) ---')
    
    # 用于存储对话历史的列表
    # 在生产环境中，你可以将其持久化到数据库（如 Redis, PostgreSQL）
    history = []
    
    # 第一轮对话
    prompt1 = "你好，我叫 Gavin，我非常喜欢 Python 编程。"
    print(f"\nUser: {prompt1}")
    
    result1 = await agent.run(prompt1, message_history=history)
    print(f"Agent: {result1.output}")
    
    # 更新历史记录：result1.all_messages() 包含了这一轮的请求和响应
    history = result1.all_messages()
    
    # 第二轮对话：测试 Agent 是否记得我的名字
    prompt2 = "你还记得我叫什么吗？"
    print(f"\nUser: {prompt2}")
    
    result2 = await agent.run(prompt2, message_history=history)
    print(f"Agent: {result2.output}")
    
    # 再次更新历史记录
    history = result2.all_messages()
    
    # 第三轮对话：测试 Agent 是否记得我的偏好
    prompt3 = "基于我的兴趣，给我推荐一个学习项目。"
    print(f"\nUser: {prompt3}")
    
    result3 = await agent.run(prompt3, message_history=history)
    print(f"Agent: {result3.output}")

    # --- 🤖 示例解读：Memory (记忆) 机制 ---
    # 1. 无状态到有状态：LLM 每次 API 调用都是独立的。
    # 2. 历史回传：PydanticAI 通过 all_messages() 获取完整的对话链，并在下一次请求时通过 message_history 传回给 LLM。
    # 3. 语义连贯性：正是因为有了 history，Agent 才能在第三轮回答中提到“Python 编程项目”。

    # 【架构师笔记：记忆管理的艺术】
    # 1. 令牌成本 (Token Cost)：记忆越长，每次请求发送的 input_tokens 就越多。
    # 2. 窗口管理 (Context Window)：对于超长对话，需要实现“滑动窗口”或“总结压缩”策略，只保留最重要的记忆。
    # 3. 持久化层：本示例使用的是内存列表。在分布式应用中，应使用数据库存储 history，并根据 sessionId 进行加载。

if __name__ == '__main__':
    asyncio.run(main())
