"""
模式 C (升级版)：移交模式 (Handoffs with Shared Context)

提升点：
1. 共享会话状态：使用 Deps 模拟一个共享的“会话记忆盒”。
2. 平滑上下文移交：Agent A 处理的信息（如用户 ID、已确认的事实）会存入状态，Agent B 接手时能立即感知。
3. 角色化隔离：展示如何通过不同的 System Prompt 配合共享状态实现专业分工。
"""
import asyncio
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, List
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

# 环境配置
root = Path(__file__).resolve().parents[1]
sys.path.append(str(root))
from common.models import get_model

# 1. 定义共享会话状态
# 【教练笔记】：这是典型的“移交模式 (Handoffs)”。
# 这是 [OpenAI Swarm](https://github.com/openai/swarm) 的核心架构设计。
# 在 Swarm 中，Agent 之间通过简单的 `transfer_to_agent` 进行交接。
# 这里的升级点在于：我们通过 PydanticAI 的 Deps 维护了一个共享状态，
# 解决了 Swarm 在原生状态下较难处理的“长效记忆和上下文平滑传递”问题。
# 共享状态就像是一个病历本，记录了之前所有 Agent 确认过的信息。
@dataclass
class SessionState:
    user_name: str
    issue_category: str = ""
    confirmed_facts: List[str] = field(default_factory=list)
    history: List[str] = field(default_factory=list)

# 2. 定义分拣结果模型
class TriageResult(BaseModel):
    next_agent: Literal["tech_support", "billing", "done"]
    summary_for_next: str

# 3. 定义各个 Agent
# 共享同一套 SessionState 依赖
tech_agent = Agent(
    get_model(), 
    deps_type=SessionState,
    system_prompt="你是一个技术专家。请查看会话历史和已确认事实，直接切入正题解决技术 Bug。"
)

billing_agent = Agent(
    get_model(), 
    deps_type=SessionState,
    system_prompt="你是一个财务专家。请基于已确认的账单事实，处理退款或订阅问题。"
)

triage_agent = Agent(
    get_model(),
    deps_type=SessionState,
    output_type=TriageResult,
    system_prompt=(
        "你是一个分拣中心。你的任务是分析用户问题，并填充 SessionState 中的初步信息。"
        "提取用户的核心诉求作为 summary_for_next。"
    )
)

async def run_handoff_workflow(user_query: str):
    # 初始化会话状态
    session = SessionState(user_name="张先生")
    print(f"🚀 [移交模式-升级版] 用户 {session.user_name} 发起咨询: {user_query}")

    # 第一步：分拣并记录初步信息
    triage_run = await triage_agent.run(user_query, deps=session)
    decision = triage_run.output
    
    # 更新共享状态（模拟分拣员的记录动作）
    session.issue_category = decision.next_agent
    session.confirmed_facts.append(f"用户核心诉求: {decision.summary_for_next}")
    
    print(f"🏷️ 分拣完成 -> 移交给: {decision.next_agent}")
    print(f"📝 备注信息: {decision.summary_for_next}")

    # 第二步：平滑移交
    if decision.next_agent == "tech_support":
        print("➡️ 技术专家接手...")
        result = await tech_agent.run(
            f"请处理此技术请求。背景信息: {decision.summary_for_next}",
            deps=session
        )
    elif decision.next_agent == "billing":
        print("➡️ 财务专家接手...")
        result = await billing_agent.run(
            f"请处理此财务请求。背景信息: {decision.summary_for_next}",
            deps=session
        )
    else:
        print("✅ 无需移交。")
        return

    print("\n" + "="*50)
    print(f"👨‍🔧 专家最终处理意见：")
    print(result.output)
    print("="*50)

if __name__ == "__main__":
    # 测试：带有复杂背景的财务移交
    asyncio.run(run_handoff_workflow("我发现去年的年度订阅多扣了199元，但我现在的账号显示是基础版，请帮我核实退款"))
