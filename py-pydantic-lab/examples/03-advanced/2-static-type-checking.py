"""
示例 03-advanced/2-static-type-checking.py: 静态类型检查 (Static Type Checking)

核心价值：开发期的“安全网”
PydanticAI 是围绕 Python 的 Generic 类型构建的。
它能在你写代码时（而不是运行代码时）就发现依赖不匹配、返回类型错误等问题。
"""

import sys
from pathlib import Path
from pydantic import BaseModel
from pydantic_ai import Agent

# 将 examples 目录添加到 sys.path
examples_root = Path(__file__).resolve().parents[1]
if str(examples_root) not in sys.path:
    sys.path.append(str(examples_root))

from common.models import get_model

# 1. 定义严格的输入输出模型
class MyDeps(BaseModel):
    api_key: str

class MyResult(BaseModel):
    summary: str
    score: int

# 2. 强类型初始化
# Agent[DepsType, ResultType]
# 这确保了所有 run 调用必须提供 MyDeps，且返回值必须能解析为 MyResult
agent: Agent[MyDeps, MyResult] = Agent(
    get_model(),
    deps_type=MyDeps,
    output_type=MyResult,
    system_prompt="评价用户的输入并给出评分。"
)

async def main():
    print('--- 示例: 静态类型检查 ---')
    
    deps = MyDeps(api_key="secret-123")
    
    # 正确调用：类型匹配
    result = await agent.run("Python 是世界上最好的语言", deps=deps)
    print(f"Summary: {result.output.summary}")
    print(f"Score: {result.output.score}")

    # --- 架构师演示：如果这里写错了会发生什么？ ---
    
    # 错误示例 1: 忘记传 deps (IDE 会在这里标红)
    # await agent.run("hello")  
    # 报错: Argument "deps" to "run" of "Agent" has incompatible type "None"; expected "MyDeps"
    
    # 错误示例 2: 访问不存在的属性 (IDE 会在这里标红)
    # print(result.output.non_existent_field)
    # 报错: "MyResult" has no attribute "non_existent_field"

    # 【架构师笔记：为什么强类型对 AI 极其重要？】
    # 1. 协作契约：在大型项目中，定义好 Agent 的泛型参数就是定义了接口契约。
    # 2. 自动补全：由于类型确定，你可以享受到全方位的代码提示，而不是对着一堆 JSON 盲猜。
    # 3. 提前发现错误：90% 的低级错误（如拼写错误、遗漏参数）在运行前就能通过 mypy/pyright 发现。

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
