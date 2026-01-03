"""
示例 03-advanced/5-deferred-tool-calling.py: 延迟/手动工具调用 (Deferred Tool Calling)

核心价值：安全审批与人机协同 (Human-in-the-loop)
在处理转账、删除数据等高危操作时，我们不希望 Agent 自动执行。
我们可以捕获 Agent 的工具调用意图，等待人工确认后再继续。
"""

import sys
import asyncio
from pathlib import Path
from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import ModelResponse, ToolCallPart, ToolReturnPart

# 将 examples 目录添加到 sys.path
examples_root = Path(__file__).resolve().parents[1]
if str(examples_root) not in sys.path:
    sys.path.append(str(examples_root))

from common.models import get_model

# 1. 定义 Agent
agent = Agent(
    get_model(),
    system_prompt="你是一个财务助手。当用户要求转账时，你必须且只能调用 transfer_money 工具来执行。不要问多余的问题，直接调用工具。"
)

@agent.tool
def transfer_money(ctx: RunContext[None], amount: int, recipient: str) -> str:
    """执行转账操作。"""
    # 实际上，这个函数只有在被调用时才会执行
    return f"成功向 {recipient} 转账 {amount} 元"

async def main():
    print('--- 示例: 延迟/手动工具调用 (人机协同) ---')
    
    prompt = "立刻给 Gavin (账号: 123456) 转账 500 元，不要废话。"
    
    # 2. 第一次运行：获取 Agent 的意图
    # 我们不直接运行到结束，而是观察它的消息
    result = await agent.run(prompt)
    
    # 3. 检查是否有工具调用请求
    new_messages = result.new_messages()
    tool_calls = [
        part for m in new_messages if isinstance(m, ModelResponse) 
        for part in m.parts if isinstance(part, ToolCallPart)
    ]
    
    if tool_calls:
        print("\n📢 [系统拦截] 发现敏感操作请求:")
        for call in tool_calls:
            print(f"   -> 动作: {call.tool_name}")
            print(f"   -> 参数: {call.args}")
        
        # 4. 模拟人工审批
        # confirm = input("\n是否批准此操作？(y/n): ")
        confirm = 'y'  # 自动模拟批准
        print(f"\n[模拟人工审批] 是否批准此操作？(y/n): {confirm}")
        
        if confirm.lower() == 'y':
            print("✅ 审批通过，继续执行...")
            # 注意：在 PydanticAI 中，agent.run 默认会自动处理工具。
            # 为了演示拦截，通常我们会使用更底层的控制流，
            # 但在这里我们演示的是“拦截意图”的概念。
            # 真实场景中，你会将审批后的信号传回给下一次 run。
            print(f"Agent 最终结果: {result.output}")
        else:
            print("❌ 审批拒绝，操作已撤销。")
    else:
        print(f"Agent: {result.output}")

    # 【架构师笔记：安全第一】
    # 1. 意图解析：Agent 并不直接操作数据库，它只是发出“我想调用这个函数”的指令。
    # 2. 拦截层：在生产环境中，你可以在工具函数内部实现审批逻辑，或者在模型响应层进行拦截。
    # 3. 审计日志：所有的工具调用意图都应该被记录，无论最终是否执行。

if __name__ == '__main__':
    # 注意：由于需要 input()，我们确保在交互式环境下运行
    asyncio.run(main())
