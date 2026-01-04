"""
模式 F：Guardrails (安全护栏与输出验证)

核心价值：
1. 结构化约束：利用 Pydantic 的校验能力防止“幻觉”数据。
2. 敏感信息脱敏：在结果输出前进行二次检查。
3. 安全代理：专门的 Agent 负责审计主要 Agent 的输出。
"""

# 【教练笔记】：这是“安全护栏模式 (Guardrails)”。
# 它的行业标杆是 NVIDIA 的 [NeMo Guardrails](https://github.com/NVIDIA/NeMo-Guardrails)。
# NeMo 使用 Colang 来定义边界，而我们在这里展示了如何使用“Pydantic 校验 + 审计 Agent”的组合，
# 在不需要学习新语言的前提下，利用 PydanticAI 实现类似的数据安全审查能力。
import asyncio
import sys
from pathlib import Path
from pydantic import BaseModel, Field, field_validator
from pydantic_ai import Agent

# 环境配置
root = Path(__file__).resolve().parents[1]
sys.path.append(str(root))
from common.models import get_model

# 1. 定义带强约束的输出模型
class CustomerRecord(BaseModel):
    name: str
    email: str
    # 使用 Pydantic 校验防止格式错误
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str):
        if "@" not in v:
            raise ValueError("邮件格式不正确")
        return v

# 2. 定义主执行 Agent
business_agent = Agent(
    get_model(),
    output_type=CustomerRecord,
    system_prompt="你是一个数据录入员。提取客户的姓名和邮箱。"
)

# 3. 定义安全审查 Agent
security_agent = Agent(
    get_model(),
    system_prompt=(
        "你是一个安全审计员。检查输入的内容是否包含敏感信息（如密码、身份证号）。"
        "如果安全，回复 'SAFE'。如果包含敏感信息，回复 'UNSAFE' 并说明原因。"
    )
)

async def run_secure_workflow(query: str):
    print(f"🔒 正在安全处理请求: {query}")
    
    # 步骤 1：生成结果
    try:
        run_result = await business_agent.run(query)
        record = run_result.output
        print(f"✅ 数据提取成功: {record}")
    except Exception as e:
        print(f"❌ 数据验证失败: {e}")
        return

    # 步骤 2：安全审计
    audit_result = await security_agent.run(f"请审计以下数据: {record.model_dump_json()}")
    
    if "SAFE" in audit_result.output:
        print("🛡️ 安全审计通过。")
        # 存入数据库...
    else:
        print(f"🚨 安全审计未通过！内容可能包含风险。")
        print(f"理由: {audit_result.output}")

if __name__ == "__main__":
    # 测试场景 1：正常数据
    # asyncio.run(run_secure_workflow("我是小王，邮箱是 xiaowang@example.com"))
    
    # 测试场景 2：带风险数据（模拟用户在对话中无意透露敏感信息）
    asyncio.run(run_secure_workflow("我是老李，我的邮箱是 laoli@example.com，我的银行卡号是 6222 0000 1111 2222"))
