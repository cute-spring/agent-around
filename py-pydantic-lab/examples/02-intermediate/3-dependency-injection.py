"""
示例 02-intermediate/3-dependency-injection.py: 依赖注入 (Dependency Injection)

核心价值：解耦与可测试性
在真实项目中，Agent 往往需要访问数据库、外部 API 或配置信息。
如果直接在工具函数中硬编码这些对象，代码将难以测试和维护。
PydanticAI 通过 RunContext 和 deps 参数实现了优雅的依赖注入。
"""

import sys
import asyncio
from dataclasses import dataclass
from pathlib import Path
from pydantic_ai import Agent, RunContext

# 将 examples 目录添加到 sys.path
examples_root = Path(__file__).resolve().parents[1]
if str(examples_root) not in sys.path:
    sys.path.append(str(examples_root))

from common.models import get_model

# 1. 定义依赖结构 (Dependencies)
# 使用 dataclass 定义 Agent 运行所需的外部资源
@dataclass
class MyDeps:
    db_connection: str
    api_key: str
    user_id: int

# 2. 初始化 Agent
# 注意：Agent[MyDeps, str] 这里的 MyDeps 声明了该 Agent 期望的依赖类型
agent = Agent(
    get_model(),
    deps_type=MyDeps,
    system_prompt="你是一个能够查询用户信息的助手。"
)

# 3. 在工具中使用依赖
# 通过 RunContext[MyDeps] 访问注入的依赖
@agent.tool
async def get_user_balance(ctx: RunContext[MyDeps]) -> str:
    """查询当前用户的账户余额。"""
    # 核心价值体现：从 ctx.deps 中获取外部资源，而不是全局变量
    db = ctx.deps.db_connection
    uid = ctx.deps.user_id
    
    print(f"--- [日志] 正在连接数据库: {db}，查询用户: {uid} ---")
    
    # 模拟数据库查询
    return f"用户 {uid} 的余额为 1000 元 (查询自 {db})"

async def main():
    print('--- 示例: 依赖注入 (Dependency Injection) ---')
    
    # 4. 准备具体的依赖实例
    # 在生产环境中，这可能是一个真实的数据库连接池
    # 在测试环境中，这可以是一个 Mock 对象
    prod_deps = MyDeps(
        db_connection="postgresql://prod_db:5432/main",
        api_key="sk-real-123",
        user_id=888
    )
    
    prompt = "帮我查一下我的余额。"
    print(f"\nPrompt: {prompt}")
    
    # 5. 运行 Agent 时注入依赖
    # 核心价值：同一个 Agent 逻辑，通过注入不同的 deps 即可切换运行环境
    result = await agent.run(prompt, deps=prod_deps)
    print(f"Agent: {result.output}")

    # --- 🤖 示例解读：Dependency Injection (DI) 机制 ---
    # 1. 类型安全：通过 Agent[MyDeps, ...] 确保了工具函数在编写时就有完善的 IDE 补全和类型检查。
    # 2. 运行上下文：RunContext 是一个容器，它承载了当前请求的所有状态（包括依赖、历史记录等）。
    # 3. 彻底解耦：get_user_balance 函数不再依赖任何全局变量，它只关心 ctx.deps 提供的接口。

    # 【架构师笔记：为什么要用 DI？】
    # 1. 易于测试：你可以轻松注入一个 MockDeps(db_connection="sqlite://:memory:") 来进行单元测试。
    # 2. 线程安全：每个 run() 调用都有自己独立的 RunContext，避免了并发环境下的资源冲突。
    # 3. 关注点分离：Agent 负责“决策逻辑”，而 Deps 负责“资源访问”，两者互不干扰。

if __name__ == '__main__':
    asyncio.run(main())
