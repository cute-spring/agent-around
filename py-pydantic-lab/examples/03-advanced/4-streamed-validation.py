"""
示例 03-advanced/4-streamed-validation.py: 流式验证 (Streamed Validation)

核心价值：及时止损，快速响应
当模型生成长文本时，如果等到全部生成完再验证，会浪费 Token 和时间。
流式验证允许我们在数据流传输过程中就开始验证。
"""

import sys
from pathlib import Path
from pydantic_ai import Agent, ModelRetry

# 将 examples 目录添加到 sys.path
examples_root = Path(__file__).resolve().parents[1]
if str(examples_root) not in sys.path:
    sys.path.append(str(examples_root))

from common.models import get_model

# 1. 定义 Agent
agent = Agent(
    get_model(),
    system_prompt="请为用户写一首简短的诗。注意：绝对不能包含 '悲伤' 这个词。"
)

# 2. 定义验证逻辑
@agent.output_validator
def validate_poetry(content: str) -> str:
    print(f"--- [后台验证] 正在检查关键词... ---")
    if "悲伤" in content:
        print("❌ 发现违禁词 '悲伤'，触发重试！")
        raise ModelRetry("诗中包含了违禁词 '悲伤'，请重写一首充满阳光的诗。")
    return content

async def main():
    print('--- 示例: 流式验证 ---')
    
    prompt = "写一首关于秋天的诗。"
    
    # 3. 使用 run_stream 进行流式处理
    async with agent.run_stream(prompt) as result:
        print("Agent 开始生成 (流式):")
        async for message in result.stream_text():
            # 这里打印的是未经最终验证的增量文本
            print(message, end="", flush=True)
        print("\n\n--- 流式传输结束，进行最终结构验证 ---")
        
        # 4. 获取最终验证后的数据
        # 在 pydantic-ai 中，流式结束后的最终结果可以通过 result.all_messages() 或直接使用流的结果
        print(f"\n最终验证通过！")

    # 【架构师笔记：流式验证 vs 最终验证】
    # 1. 用户体验：用户可以立刻看到文本闪烁，而验证在后台确保质量。
    # 2. 自动重试：如果验证失败，PydanticAI 会保留对话历史并自动向 LLM 发送错误信息进行重试。
    # 3. 适用场景：适用于长文本生成、敏感词过滤、以及复杂的业务逻辑校验。

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
