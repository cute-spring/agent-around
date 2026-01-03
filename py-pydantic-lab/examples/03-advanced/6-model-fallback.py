"""
示例 03-advanced/6-model-fallback.py: 模型回退策略 (Model Fallback)

核心价值：高可用性与成本优化
单一模型可能会遇到停机、限流 (Rate Limit) 或解析失败。
回退策略确保在首选模型失败时，能够自动切换到备选模型。
"""

import sys
import asyncio
from pathlib import Path
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.providers.ollama import OllamaProvider

# 将 examples 目录添加到 sys.path
examples_root = Path(__file__).resolve().parents[1]
if str(examples_root) not in sys.path:
    sys.path.append(str(examples_root))

from common.models import get_model

async def run_with_fallback(prompt: str):
    # 1. 定义候选模型列表
    # 优先级 1: DeepSeek (性价比之王)
    # 优先级 2: GPT-4o-mini (稳定备选)
    # 优先级 3: Ollama (本地兜底)
    models = [
        ("DeepSeek", get_model()), # 默认工厂函数返回的模型
        ("GPT-4o-mini", OpenAIChatModel("gpt-4o-mini")), 
        ("Local-Ollama", OpenAIChatModel("qwen2.5-coder", provider=OllamaProvider(base_url="http://localhost:11434/v1")))
    ]
    
    last_error = None
    
    for name, model in models:
        try:
            print(f"--- 尝试使用模型: {name} ---")
            agent = Agent(model)
            result = await agent.run(prompt)
            print(f"✅ {name} 调用成功！")
            return result.output
        except Exception as e:
            print(f"❌ {name} 失败: {str(e)}")
            last_error = e
            continue
            
    print("‼️ 所有模型均已失败")
    raise last_error

async def main():
    print('--- 示例: 模型回退策略 ---')
    
    try:
        response = await run_with_fallback("请写一句关于人工智能的格言。")
        print(f"\n最终响应: {response}")
    except Exception as e:
        print(f"任务最终失败: {e}")

    # 【架构师笔记：多模型策略】
    # 1. 容错性：API 抖动是常态，多模型回退是构建工业级 AI 应用的必备。
    # 2. 成本平衡：可以先尝试用便宜的模型（如 GPT-4o-mini），如果失败或质量达不到要求，再换贵的（如 GPT-4o）。
    # 3. 混合云架构：云端模型（高效）与本地模型（隐私/兜底）结合。

if __name__ == '__main__':
    asyncio.run(main())
