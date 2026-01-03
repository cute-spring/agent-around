"""
示例 03-advanced/1-dynamic-system-prompt.py: 动态系统提示词 (Dynamic System Prompts)

核心价值：上下文感知的人设
静态的 system_prompt 无法感知运行时的变化。
通过 @agent.system_prompt 装饰器，我们可以根据注入的依赖 (Deps) 动态构建提示词。
"""

import sys
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
from pydantic_ai import Agent, RunContext

# 将 examples 目录添加到 sys.path
examples_root = Path(__file__).resolve().parents[1]
if str(examples_root) not in sys.path:
    sys.path.append(str(examples_root))

from common.models import get_model

@dataclass
class UserContext:
    user_name: str
    user_role: str  # 'admin' or 'guest'

# 1. 初始化 Agent
agent = Agent(
    get_model(),
    deps_type=UserContext,
)

# 2. 定义动态系统提示词
@agent.system_prompt
def get_system_prompt(ctx: RunContext[UserContext]) -> str:
    # 根据运行时注入的 UserContext 动态生成提示词
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    role_instruction = (
        "你拥有最高权限，可以回答任何敏感问题。" 
        if ctx.deps.user_role == 'admin' 
        else "你是一个受限助手，请保持礼貌并拒绝越权操作。"
    )
    
    return f"""
    你的名字是 AI 助手。
    当前用户: {ctx.deps.user_name}
    用户角色: {ctx.deps.user_role}
    当前时间: {now}
    权限指令: {role_instruction}
    """

async def main():
    print('--- 示例: 动态系统提示词 ---')
    
    # 场景 1: 管理员访问
    admin_ctx = UserContext(user_name="Gavin", user_role="admin")
    print("\n[场景 1: 管理员]")
    result1 = await agent.run("我现在的权限能做什么？", deps=admin_ctx)
    print(f"Agent: {result1.output}")
    
    # 场景 2: 普通访客访问
    guest_ctx = UserContext(user_name="访客小王", user_role="guest")
    print("\n[场景 2: 普通访客]")
    result2 = await agent.run("我现在的权限能做什么？", deps=guest_ctx)
    print(f"Agent: {result2.output}")

    # 【架构师笔记：动态提示词的优势】
    # 1. 最小权限原则：不需要在静态 Prompt 中写死所有逻辑，而是按需注入。
    # 2. 减少 Token 浪费：只在提示词中包含与当前上下文相关的信息。
    # 3. 实时性：可以感知时间、地理位置等实时变化的外部状态。

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
