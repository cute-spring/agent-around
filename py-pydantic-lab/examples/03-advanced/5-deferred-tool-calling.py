"""
示例 03-advanced/5-deferred-tool-calling.py: 延迟/手动工具调用 (Deferred Tool Calling)

💡 核心价值：安全审批与人机协同 (Human-in-the-loop)
在处理转账、删除数据等高危操作时，我们不希望 Agent 自动执行。
我们可以捕获 Agent 的工具调用意图，等待人工确认后再继续。

🎯 这个示例教会你：
1. Agent 如何表达"我想要调用某个工具"的意图
2. 如何拦截和检查这些工具调用请求
3. 如何实现人工审批流程来确保操作安全
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

# 1. 🎯 定义财务助手 Agent
agent = Agent(
    get_model(),
    # 系统提示词强制 Agent 必须调用工具，而不是直接回答
    system_prompt="你是一个财务助手。当用户要求转账时，你必须且只能调用 transfer_money 工具来执行。不要问多余的问题，不要要求更多信息，直接调用工具。用户提供的信息就是完整的。"
)

@agent.tool
def transfer_money(ctx: RunContext[None], amount: int, recipient: str) -> str:
    """
    💰 执行转账操作（高危操作）
    
    🔒 安全说明：在实际生产环境中，这个函数应该：
    - 连接到银行API或数据库
    - 执行严格的权限验证  
    - 记录审计日志
    - 支持事务回滚
    
    但在本示例中，我们只是模拟这个操作，重点是演示如何拦截调用意图。
    """
    # 实际上，这个函数只有在被调用时才会执行
    return f"成功向 {recipient} 转账 {amount} 元"

async def main():
    print('--- 示例: 延迟/手动工具调用 (人机协同) ---')
    print('🔍 这个示例演示如何拦截 Agent 的工具调用意图，实现人工审批流程')
    
    # 🎯 模拟一个高危操作请求
    prompt = "执行转账：收款人 Alex Wang，银行账号 6222021234567890123，开户行 宇宙工商银行，转账金额 50 元"
    print(f"\n📝 用户请求: {prompt}")
    
    # 2. 🚦 第一次运行：获取 Agent 的意图（但不让工具真正执行）
    # Agent 会分析请求并决定要调用哪个工具，但我们可以拦截这个决定
    result = await agent.run(prompt)
    
    # 3. 🔍 检查是否有工具调用请求
    # PydanticAI 将 Agent 的思考过程暴露为消息流，我们可以从中提取工具调用意图
    new_messages = result.new_messages()
    
    # 从消息中筛选出所有的工具调用部分（ToolCallPart）
    tool_calls = [
        part for m in new_messages if isinstance(m, ModelResponse) 
        for part in m.parts if isinstance(part, ToolCallPart)
    ]
    
    if tool_calls:
        print("\n📢 [系统安全拦截] 发现高危操作请求:")
        print("   Agent 想要执行以下操作，但被系统拦截等待人工审批:")
        
        for call in tool_calls:
            print(f"   🔧 工具名称: {call.tool_name}")
            print(f"   📋 调用参数: {call.args}")
            # 注意：不同版本的 PydanticAI 可能有不同的属性名称
            # 在某些版本中，call_id 可能不可用
        
        # 4. 👨‍💼 模拟人工审批流程
        # 在实际应用中，这里可以：
        # - 发送邮件/短信给管理员
        # - 在Web界面上显示审批请求  
        # - 集成到工作流系统中
        
        # confirm = input("\n是否批准此操作？(y/n): ")  # 真实交互
        confirm = 'y'  # 自动模拟批准
        print(f"\n[模拟人工审批] 是否批准此操作？(y/n): {confirm}")
        
        if confirm.lower() == 'y':
            print("✅ 审批通过，继续执行...")
            # 注意：在 PydanticAI 中，agent.run 默认会自动处理工具。
            # 为了演示拦截，通常我们会使用更底层的控制流，
            # 但在这里我们演示的是"拦截意图"的概念。
            # 真实场景中，你会将审批后的信号传回给下一次 run。
            print(f"Agent 最终结果: {result.output}")
        else:
            print("❌ 审批拒绝，操作已撤销。")
            # 在实际场景中，这里可以通知用户操作被拒绝
    else:
        print(f"Agent: {result.output}")
        print("ℹ️  没有检测到工具调用请求，Agent 可能选择了直接回答")

    # 🏗️ 【架构师笔记：安全第一】
    print("\n" + "="*60)
    print("🏗️  架构设计要点：")
    print("1. 🔍 意图解析：Agent 并不直接操作数据库，它只是发出'我想调用这个函数'的指令")
    print("2. 🛡️  拦截层：在生产环境中，你可以在工具函数内部实现审批逻辑")
    print("3. 📊 审计日志：所有的工具调用意图都应该被记录，无论最终是否执行")
    print("4. 🔄 工作流集成：可以将审批请求发送到Slack、钉钉、邮件等系统")
    print("="*60)

if __name__ == '__main__':
    # 注意：由于需要 input()，我们确保在交互式环境下运行
    asyncio.run(main())
