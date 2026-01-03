"""
示例 3: 结构化输出 (Structured Output)

核心价值：强类型约束与自动解析 (Type Safety & Auto-parsing)
SDK 通过 Pydantic 模型强制 AI 遵循定义的 Schema。
这让 AI 的输出可以直接被程序逻辑使用，而不会因为格式错误崩溃。
"""

import sys
from typing import List
from pathlib import Path
from pydantic import BaseModel, Field
from pydantic_ai import Agent

# 将 examples 目录添加到 sys.path 以允许从 common 导入
examples_root = Path(__file__).resolve().parents[1]
if str(examples_root) not in sys.path:
    sys.path.append(str(examples_root))

from common.models import get_model

# 1. 定义输出的“形状” (Schema)
class Ingredient(BaseModel):
    name: str = Field(description="食材名称")
    amount: str = Field(description="用量")

class Recipe(BaseModel):
    name: str = Field(description="菜名")
    ingredients: List[Ingredient]
    steps: List[str] = Field(description="制作步骤")

# 2. 初始化 Agent
# Architectural Note: 通过 output_type 声明期望的返回类型
agent = Agent(
    get_model(),
    output_type=Recipe,  # 在 pydantic-ai v1.x 中，使用 output_type
    system_prompt="You are a helpful cooking assistant."
)

def main():
    print('--- 示例 3: 强类型结构化输出 ---')
    
    prompt = '帮我生成一个巧克力饼干的简单食谱。'
    print(f"Prompt: {prompt}\n")
    
    # 3. 运行 Agent
    # 核心价值体现：result.output 已经是 Recipe 类型的实例，无需手动解析 JSON
    result = agent.run_sync(prompt)
    recipe = result.output
    
    print("生成的结构化数据:")
    print(f"菜名: {recipe.name}")
    print("\n食材:")
    for ing in recipe.ingredients:
        print(f"- {ing.name}: {ing.amount}")
    
    print("\n步骤:")
    for i, step in enumerate(recipe.steps, 1):
        print(f"{i}. {step}")
    
    # 打印 Token 使用情况
    # 【架构师笔记：深度解读 Token 消耗】
    # 1. input_tokens (输入): 包含你的 Prompt + PydanticAI 自动生成的 System Prompt (JSON Schema 定义)。
    # 2. cache_read_tokens (缓存命中): 
    #    - 在重复运行时，你会发现此数值很高（接近 input_tokens）。
    #    - 这是因为稳定的 System Prompt 触发了 LLM 服务商（如 DeepSeek）的缓存机制。
    #    - 核心价值：极大降低响应延迟 (Latency) 并节省 API 费用。
    # 3. output_tokens (输出): 纯粹的结构化食谱内容的长度。
    # 4. requests=1: PydanticAI 实现了“一步到位”的结构化提取，无需多次往返。
    #
    # --- 教练的总结 ---
    # 这份数据证明了你的架构模式是高效的：
    # 1. 利用了结构化输出的确定性：虽然 System Prompt 变长了，但由于其高度重复性，触发了缓存机制。
    # 2. 低成本、高性能：通过 Pydantic 模型定义的复杂约束，在缓存的加持下，变成了近乎“零成本”的输入。
    # 这就是为什么在生产环境下，我们极力推荐使用 PydanticAI 这种能生成稳定 System Prompt 的框架，
    # 因为它对 LLM 服务商的缓存机制极其友好。
    print(f"\nToken 使用情况: {result.usage()}")

if __name__ == '__main__':
    main()
