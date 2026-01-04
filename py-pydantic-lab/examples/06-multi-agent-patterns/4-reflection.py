"""
模式 D (升级版)：反思模式 (Reflection with Multi-dimensional Review)

提升点：
1. 结构化反馈：将“打回重做”的标准细化为多个评分维度（创意、逻辑、合规）。
2. 历史记忆：Worker 在修改时，能看到之前的“所有失败版本”和反馈。
3. 退出保护：增加最大迭代限制，防止 Token 消耗失控。
"""
import asyncio
import sys
from pathlib import Path
from typing import List
from pydantic import BaseModel, Field
from pydantic_ai import Agent

# 环境配置
root = Path(__file__).resolve().parents[1]
sys.path.append(str(root))
from common.models import get_model

# 1. 定义多维度评审模型
# 【教练笔记】：这是“反思模式 (Reflection)”。
# 它是 [AutoGPT](https://github.com/Significant-Gravitas/AutoGPT) 能够实现自主循环的核心逻辑。
# 通过引入一个独立的 Reviewer Agent，我们强迫系统跳出“一次性输出”的局限。
# 在 PydanticAI 中，利用 output_type 强约束反馈数据，比 AutoGPT 的纯文本解析更加稳定。
class ReviewFeedback(BaseModel):
    creativity_score: int = Field(ge=1, le=10, description="创意分 (1-10)")
    logic_score: int = Field(ge=1, le=10, description="逻辑分 (1-10)")
    is_perfect: bool = Field(description="是否达到发布标准")
    suggestions: str = Field(description="具体的修改建议")

# 2. 定义 Worker 和 Critic
copywriter = Agent(
    get_model(), 
    system_prompt=(
        "你是一个顶尖的广告文案。你需要创作出让人过目不忘的口号。"
        "你会收到之前的反馈，请根据反馈不断优化。"
    )
)

critic = Agent(
    get_model(),
    output_type=ReviewFeedback,
    system_prompt=(
        "你是一个极其苛刻的创意总监。请根据以下维度评分：\n"
        "1. 创意性：是否新颖，不落俗套。\n"
        "2. 逻辑性：是否直击痛点，符合常识。\n"
        "只有当所有维度都表现优异且 is_perfect 为 True 时，文案才算通过。"
    )
)

async def run_reflection(topic: str, max_rounds: int = 3):
    print(f"🚀 [反思模式-升级版] 开始为主题 '{topic}' 创作口号...")
    
    current_content = "初始文案待生成"
    history_logs = []  # 记录每一轮的改进过程
    
    for round_num in range(1, max_rounds + 1):
        print(f"\n--- 🔄 第 {round_num} 轮迭代 ---")
        
        # 步骤 1: 创作 (带历史记忆)
        context = "\n".join(history_logs) if history_logs else "这是第一次尝试。"
        write_prompt = f"主题: {topic}\n历史改进建议: \n{context}\n请基于以上反馈，给出更好版本的口号。"
        
        write_result = await copywriter.run(write_prompt)
        current_content = write_result.output
        print(f"✍️ 最新版本: {current_content}")
        
        # 步骤 2: 多维度审阅
        review_result = await critic.run(f"请审阅此文案: {current_content}")
        feedback = review_result.output
        
        print(f"📊 评分 -> 创意: {feedback.creativity_score} | 逻辑: {feedback.logic_score}")
        
        if feedback.is_perfect:
            print("✨ 【通过】创意总监已批准！")
            break
        else:
            print(f"❌ 【未通过】建议: {feedback.suggestions}")
            # 将本轮的失败教训存入历史
            history_logs.append(f"第{round_num}轮文案: {current_content} -> 反馈: {feedback.suggestions}")
            
        if round_num == max_rounds:
            print("⚠️ 达到最大迭代次数，取当前最佳版本。")
            
    print("\n" + "="*50)
    print(f"🏆 最终定稿：{current_content}")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(run_reflection("一款能够检测情绪并自动播放相应音乐的耳机"))
