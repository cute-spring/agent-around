"""
示例 02-intermediate/1-reflection.py: 反思与自我纠错 (Reflection)

核心价值：提升 Agent 的可靠性
在复杂的任务中，LLM 可能会产生幻觉或违反业务逻辑。
PydanticAI 提供了 output_validator 机制，允许我们在 LLM 输出后进行“审校”。
如果审校不通过，Agent 会收到错误反馈并自动重新尝试（Retry），直到满足条件。
"""

import sys
from pathlib import Path
from pydantic import BaseModel, Field, field_validator
from pydantic_ai import Agent, RunContext, ModelRetry

# 将 examples 目录添加到 sys.path
examples_root = Path(__file__).resolve().parents[1]
if str(examples_root) not in sys.path:
    sys.path.append(str(examples_root))

from common.models import get_model

# 1. 定义输出结构
class UserProfile(BaseModel):
    name: str
    age: int
    bio: str = Field(description="A short biography of the user.")

    @field_validator('age')
    @classmethod
    def validate_age(cls, v: int) -> int:
        if v < 0 or v > 120:
            raise ValueError("Age must be between 0 and 120.")
        return v

# 2. 初始化 Agent
# 注意：retries=3 表示如果验证失败，允许 Agent 最多尝试 3 次
agent = Agent(
    get_model(),
    output_type=UserProfile,
    retries=3,
    system_prompt=(
        "You are an expert at extracting user information from text."
        "If information is missing, make a reasonable guess based on context."
    )
)

# 3. 定义结果校验器 (Output Validator)
# 这是 Reflection 的核心：即使 Pydantic 类型检查通过了，我们还可以进行业务逻辑校验
@agent.output_validator
def validate_bio_length(ctx: RunContext[None], profile: UserProfile) -> UserProfile:
    print(f"--- 正在校验生成的简介: '{profile.bio[:30]}...' ---")
    
    # 业务逻辑：简介必须至少包含 20 个单词 (故意设高，以触发 Retry)
    word_count = len(profile.bio.split())
    if word_count < 20:
        print(f"⚠️ 校验失败: 简介太短 ({word_count} 个单词)")
        # 抛出 ModelRetry 异常，PydanticAI 会将此错误发回给 LLM 并要求其重试
        raise ModelRetry(
            f"The biography is too short (only {word_count} words). "
            "Please provide a much more detailed biography with at least 20 words."
        )
    
    print("✅ 校验通过！")
    return profile

async def main():
    print('--- 示例: 反思与自我纠错 (Reflection) ---')
    
    # 故意提供一个可能导致初次生成失败的指令
    prompt = "Extract info for: John Doe, 25 years old. He likes coding. Give me a very short one sentence bio."
    
    print(f"Prompt: {prompt}\n")
    
    # 运行 Agent
    result = await agent.run(prompt)
    
    print("\n最终生成的结构化数据:")
    print(f"姓名: {result.output.name}")
    print(f"年龄: {result.output.age}")
    print(f"简介: {result.output.bio}")
    
    # --- 🤖 示例解读：Reflection (反思) 机制 ---
    # 1. 初始冲突：Prompt 要求“短简介”，但业务逻辑要求“至少 20 个单词”。
    # 2. 触发反思：
    #    - 第一次尝试：LLM 生成了短简介 -> 校验失败 -> 抛出 ModelRetry。
    #    - 自动修正：PydanticAI 将错误反馈发回给 LLM。
    #    - 第二次尝试：LLM 修正输出 -> 校验通过。
    # 3. 关键指标解读：
    #    - requests=2: 证明了 Agent 在幕后进行了自动重试。
    #    - cache_read_tokens: 第二次重试时，稳定的系统提示词触发了缓存，降低了成本。
    #
    # 【架构师笔记：Reflection 的威力】
    # 1. 闭环控制：Agent 不再是“一锤子买卖”，而是一个具备“感知-行动-反馈-修正”能力的闭环系统。
    # 2. 开发者意图强加：通过代码（而非仅仅通过 Prompt）来强制执行业务规则。
    # 3. 容错性：即使 LLM 第一次犯错，系统也能在用户感知不到的情况下自动修复。
    print(f"\nToken 使用情况: {result.usage()}")

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
