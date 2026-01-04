"""
模式 E：Human-in-the-Loop (人机协作/人工干预)

核心价值：
1. 风险控制：对于敏感操作（如大额转账、删除数据），Agent 必须请求人工审批。
2. 交互式反馈：Agent 可以暂停运行，等待用户提供缺失的信息或确认决策。
3. 状态挂起：展示如何模拟一个“待审核”状态。
"""

# 【教练笔记】：这是“人工介入模式 (HITL)”。
# 在 [LangGraph](https://github.com/langchain-ai/langgraph) 中，这通常通过“检查点 (Checkpoints)”和“打断 (Interrupts)”节点实现。
# 它是目前 AI 落地金融、医疗等强监管行业的“生命线”。
# 在 PydanticAI 中，我们利用 structured output 来决定是否触发人工流程，实现更灵活的控制。

import asyncio
import sys
from pathlib import Path
from pydantic import BaseModel, Field
from pydantic_ai import Agent

# 环境配置
root = Path(__file__).resolve().parents[1]
sys.path.append(str(root))
from common.models import get_model

# 1. 定义操作意图
class RefundAction(BaseModel):
    amount: float
    reason: str
    requires_approval: bool = False

# 2. 定义审核 Agent
# 它不直接退款，而是判断是否需要人工介入
approver_agent = Agent(
    get_model(),
    output_type=RefundAction,
    system_prompt=(
        "你是一个退款策略审核员。"
        "如果退款金额超过 500 元，必须设置 requires_approval 为 True。"
        "否则可以直接处理。"
    )
)

async def simulate_human_input(action: RefundAction) -> bool:
    """模拟人工审批界面"""
    print(f"\n⚠️  [人工审批请求] ⚠️")
    print(f"退款金额: ￥{action.amount}")
    print(f"退款理由: {action.reason}")
    # 在真实应用中，这里可能是发送 Webhook 或等待前端 API 调用
    # 这里我们模拟用户输入
    choice = input("是否批准该操作？(y/n): ").strip().lower()
    return choice == 'y'

async def process_refund_workflow(query: str):
    print(f"🔍 正在分析退款请求: {query}")
    
    # 第一步：Agent 分析风险
    run_result = await approver_agent.run(query)
    action = run_result.output
    
    # 第二步：根据 Agent 的判断决定是否进入人工流程
    if action.requires_approval:
        print("🚩 检测到高风险操作，正在联系管理员...")
        approved = await simulate_human_input(action)
        
        if approved:
            print("✅ 管理员已批准。正在执行退款...")
            # 执行真实的退款逻辑...
        else:
            print("❌ 管理员已拒绝。退款流程终止。")
    else:
        print(f"🚀 低风险操作，系统自动处理中... 金额: ￥{action.amount}")

if __name__ == "__main__":
    # 测试场景 1：低风险
    # asyncio.run(process_refund_workflow("帮我退了那个 20 元的手机壳，质量太差了"))
    
    # 测试场景 2：高风险（触发人工）
    asyncio.run(process_refund_workflow("我昨天买的 2000 元显示器屏幕碎了，要求全额退款"))
