"""
示例 1: 基础文本生成 (Basic Generation)

核心价值：Provider Agnostic (供应商无关性)
架构说明：通过 common.models 抽象层，Agent 逻辑与具体的模型供应商解耦。
"""

import sys
from pathlib import Path
from pydantic_ai import Agent

# 将 examples 目录添加到 sys.path 以允许从 common 导入
examples_root = Path(__file__).resolve().parents[1]
if str(examples_root) not in sys.path:
    sys.path.append(str(examples_root))

from common.models import get_model

# 初始化 Agent
# Rationale: 简单的文本生成不需要定义 output_type
agent = Agent(
    get_model(),
    system_prompt="You are a helpful assistant."
)

def main():
    print('--- 示例 1: 统一 API 调用 (基础生成) ---')
    
    prompt = '用一句话介绍 PydanticAI 的最大优势。'
    print(f"Prompt: {prompt}")
    
    # 核心价值体现：无论底层是 DeepSeek、OpenAI 还是 Ollama，代码逻辑保持一致
    result = agent.run_sync(prompt)
    
    print(f"AI 回复: {result.output}")

if __name__ == '__main__':
    main()
