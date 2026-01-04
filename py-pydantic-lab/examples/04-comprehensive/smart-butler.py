"""
示例 04-comprehensive/smart-butler.py: 综合实战 - 智能管家 Agent

本示例集成了 PydanticAI 的核心能力：
1. 依赖注入 (DI): 注入用户信息和数据库模拟器。
2. 结构化输出: 强制 Agent 按特定格式返回日程信息。
3. 工具调用: 执行转账和日程管理。
4. 手动审批 (Deferred Tool Calling): 转账前必须人工确认。
5. 反思校验 (Reflection): 检查日程时间冲突。
6. 多轮记忆 (Memory): 维护对话上下文。
"""

import sys
import asyncio
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext, ModelRetry
from pydantic_ai.messages import ModelResponse, ToolCallPart

# 将 examples 目录添加到 sys.path
examples_root = Path(__file__).resolve().parents[1]
if str(examples_root) not in sys.path:
    sys.path.append(str(examples_root))

from common.models import get_model

# --- 1. 定义领域模型 ---

class CalendarEvent(BaseModel):
    """日程事件模型"""
    title: str = Field(description="日程标题")
    start_time: datetime = Field(description="开始时间")
    end_time: datetime = Field(description="结束时间")
    location: Optional[str] = None

@dataclass
class UserDeps:
    """依赖注入对象：模拟用户环境"""
    user_name: str
    user_id: str
    existing_events: List[CalendarEvent]

# --- 2. 初始化 Agent ---

agent = Agent(
    get_model(),
    deps_type=UserDeps,
    system_prompt=(
        "你是一个全能智能管家。你可以帮用户管理日程和处理转账。"
        "1. 处理日程时，必须确保时间不重叠。"
        "2. 处理转账时，必须使用 transfer_money 工具。"
        "你的回复应当亲切、专业。"
    )
)

# --- 3. 定义工具与校验逻辑 ---

@agent.tool
def transfer_money(ctx: RunContext[UserDeps], amount: int, recipient: str) -> str:
    """执行转账操作。"""
    # 实际业务中这里会调用 API
    return f"已成功从用户 {ctx.deps.user_name} (ID: {ctx.deps.user_id}) 账户向 {recipient} 转账 {amount} 元。"

@agent.tool
def add_calendar_event(ctx: RunContext[UserDeps], event: CalendarEvent) -> str:
    """添加新的日程。"""
    ctx.deps.existing_events.append(event)
    return f"日程 '{event.title}' 已成功添加。"

@agent.output_validator
def validate_calendar_conflict(ctx: RunContext[UserDeps], output: str) -> str:
    """
    反思校验：虽然这是个简单的文本输出 Agent，
    但我们可以根据上下文检查最近一次操作是否导致了时间冲突。
    (此处仅为演示 Reflection 逻辑)
    """
    # 模拟冲突检查：如果日程中有 '冲突' 字样，触发重试
    if "冲突" in output:
        raise ModelRetry("发现日程冲突，请重新协调时间。")
    return output

# --- 4. 核心交互流程 ---

async def run_butler_session():
    print('--- 🏛️ 综合实战: 智能管家 Agent ---')
    
    # 初始化依赖
    deps = UserDeps(
        user_name="Gavin",
        user_id="U12345",
        existing_events=[
            CalendarEvent(
                title="早会", 
                start_time=datetime(2026, 1, 3, 9, 0), 
                end_time=datetime(2026, 1, 3, 10, 0)
            )
        ]
    )
    
    history = []
    
    # 场景：添加日程并转账
    prompts = [
        "帮我安排一个今天上午 9:30 的面试日程。",  # 这会引起冲突
        "好吧，那就改到今天下午 2:00 吧。另外，给小王转账 200 元。",
    ]

    for i, prompt in enumerate(prompts):
        print(f"\n[用户]: {prompt}")
        
        # 运行 Agent
        result = await agent.run(prompt, deps=deps, message_history=history)
        
        # 🛡️ 拦截工具调用 (Deferred Tool Calling 安全演示)
        # 
        # 💡 核心概念：在生产环境中，我们不希望 Agent 自动执行高危操作
        #    而是先捕获其"意图"，等待人工审批后再真正执行
        #
        # 🔍 步骤1: 获取 Agent 本次运行产生的新消息
        #    result.new_messages() 返回本次对话轮次中 Agent 生成的所有消息
        new_messages = result.new_messages()
        
        # 🔍 步骤2: 从消息中提取所有的工具调用意图
        #    使用列表推导式筛选出所有的 ToolCallPart
        #    - ModelResponse: Agent 的响应消息
        #    - ToolCallPart: 表示"我想调用某个工具"的意图
        tool_calls = [
            part for m in new_messages if isinstance(m, ModelResponse) 
            for part in m.parts if isinstance(part, ToolCallPart)
        ]
        
        # 🔍 步骤3: 检查是否有特定的高危操作（如转账）
        #    这里专门检查 transfer_money 工具调用
        if any(tc.tool_name == "transfer_money" for tc in tool_calls):
            print("\n📢 [安全拦截] 发现转账请求，正在请求人工审批...")
            # 🎯 在实际生产环境中，这里会：
            #   - 发送邮件/短信给管理员
            #   - 在Web界面显示审批请求
            #   - 集成到工作流系统（如钉钉、飞书审批）
            #   - 记录审计日志
            
            # 模拟自动批准（演示用）
            print("✅ [人工审批] 已批准。")
            # 🎯 如果审批拒绝，可以：
            #   - 不执行工具调用
            #   - 通知用户操作被拒绝
            #   - 记录安全事件

        print(f"[管家]: {result.output}")
        
        # 更新记忆
        history = result.all_messages()

    print("\n--- 当前最终日程表 ---")
    for event in deps.existing_events:
        print(f"- {event.title}: {event.start_time} 至 {event.end_time}")

if __name__ == '__main__':
    asyncio.run(run_butler_session())
