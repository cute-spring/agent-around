"""
模式 B (升级版)：委托模式 (Delegation with Dependency Injection & Context)

提升点：
1. 引入 Deps 机制：模拟从数据库或配置中读取项目背景。
2. 强化上下文：经理调用专家时，带入项目全局背景，让专家回答更精准。
3. 增加小白友好注释：解释为什么 DI (依赖注入) 对 Agent 协作至关重要。
"""
import asyncio
import sys
from dataclasses import dataclass
from pathlib import Path
from pydantic_ai import Agent, RunContext

# 环境配置
root = Path(__file__).resolve().parents[1]
sys.path.append(str(root))
from common.models import get_model

# 1. 定义共享依赖 (Dependency Injection)
# 【教练笔记】：在真实生产中，Agent 需要知道它是为哪个用户服务、在哪个项目下。
# 使用 dataclass 定义依赖，可以确保所有 Agent 共享同一套“外部世界”的信息。
@dataclass
class ProjectContext:
    project_name: str
    risk_tolerance: str  # 风险偏好：保守、激进
    investor_id: str

# 2. 定义专家 Agent
# 专家现在也知道它处于什么依赖环境中 (deps_type)
financial_expert = Agent(
    get_model(), 
    deps_type=ProjectContext,
    system_prompt="你是一个精通财报分析的专家。请结合项目背景和投资者的风险偏好给出建议。"
)

# 3. 定义主 Agent (Manager)
manager = Agent(
    get_model(),
    deps_type=ProjectContext,
    system_prompt=(
        "你是一个资深投资经理。你的职责是为当前项目提供决策建议。"
        "请务必在回答中体现出对项目背景的了解。"
        "如果涉及深层财务风险，请调用 'call_financial_expert' 工具。"
    )
)

# 4. 将专家包装为工具 (带上下文传递)
# 【教练笔记】：这是“委托模式”。
# 它与 [OpenAI Swarm](https://github.com/openai/swarm) 的思路异曲同工，但更加“Pythonic”。
# 在 Swarm 中，Agent 可以返回另一个 Agent；而在 PydanticAI 中，我们将 Agent 直接包装成 Tool。
# 这种“Agent as a Tool”的模式在 [Microsoft AutoGen](https://github.com/microsoft/autogen) 中也广泛应用，
# 让主 Agent 能根据 RunContext 动态决定何时调用专业子 Agent。
@manager.tool
async def call_financial_expert(ctx: RunContext[ProjectContext], company_name: str, question: str) -> str:
    """
    委托财务专家进行分析。专家会自动感知当前的风险偏好。
    """
    # 【教练笔记】：这里体现了 DI 的威力。
    # 经理 (Manager) 的上下文 (ctx.deps) 直接传递给专家，无需手动拼接字符串。
    print(f"🕵️ 经理决策：正在为项目 [{ctx.deps.project_name}] 咨询财务专家...")
    
    # 专家在运行阶段会通过 deps 获取外部上下文
    result = await financial_expert.run(
        f"分析公司: {company_name}, 问题: {question}",
        deps=ctx.deps
    )
    return result.output

async def main():
    # 模拟从外部（如数据库）加载的项目配置
    current_deps = ProjectContext(
        project_name="2025 稳健增长基金",
        risk_tolerance="极度保守 (不允许任何本金损失风险)",
        investor_id="INV-9527"
    )

    query = "帮我看看拼多多的财务数据，他们现在的出海战略是否有巨大的财务漏洞？"
    
    print(f"🚀 [委托模式-升级版] 开始处理任务...")
    print(f"📊 项目背景: {current_deps.project_name} | 偏好: {current_deps.risk_tolerance}")
    
    # 运行主 Agent，并注入依赖
    result = await manager.run(query, deps=current_deps)
    
    print("\n" + "="*50)
    print("📈 投资经理最终回复：")
    print(result.output)
    print("="*50)

if __name__ == "__main__":
    asyncio.run(main())
