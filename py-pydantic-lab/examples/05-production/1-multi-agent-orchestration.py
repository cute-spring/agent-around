"""
多Agent协作编排示例 - 深度注释解读版

展示如何使用Director Agent协调多个专业Worker Agent完成复杂任务。
本示例不仅展示了代码实现，还为Python初学者提供了核心概念的解读。
"""

import asyncio  # 异步I/O库，用于处理并发任务
import sys
from pathlib import Path
from typing import List, Optional  # 类型提示，List[str]表示“一串字符串”
from pydantic import BaseModel, Field
from pydantic_ai import Agent

# 将 examples 目录添加到 sys.path
examples_root = Path(__file__).resolve().parents[1]
if str(examples_root) not in sys.path:
    sys.path.append(str(examples_root))

from common.models import get_model


# ==================== 领域模型定义 (Structure Data Blueprints) ====================
# 【教练笔记】：这些类就像是给 AI 下的“订单模版”。
# 我们通过定义这些模型，强制要求 AI 必须按这个格式回话，否则程序就不收货。
# 这种“结构化输出”是 Agent 系统的基石。

class ResearchTopic(BaseModel):
    """研究主题：定义了任务分解后的基本单元"""
    name: str = Field(description="主题名称")
    description: str = Field(description="主题描述")


class DecomposedTasks(BaseModel):
    """分解后的任务列表：由分解Agent生成"""
    topics: List[ResearchTopic] = Field(description="研究主题列表")


class ResearchFinding(BaseModel):
    """研究发现：由研究Agent针对特定主题生成"""
    topic: str = Field(description="研究主题")
    key_points: List[str] = Field(description="关键发现点")
    sources: List[str] = Field(description="信息来源")


class ResearchReport(BaseModel):
    """研究报告：最终由整合Agent生成的完整文档"""
    title: str = Field(description="报告标题")
    executive_summary: str = Field(description="执行摘要")
    findings: List[ResearchFinding] = Field(description="研究发现列表")
    recommendations: List[str] = Field(description="建议措施")


# ==================== 专业Agent定义 (Agent Job Descriptions) ====================
# 【教练笔记】：在这里我们定义了三个拥有不同“岗位职责”的 Agent。
# 特别注意 output_type：它让 AI 的回复直接变成 Python 对象，省去了解析字符串的痛苦。

# 1. 任务分解Agent - 职责：将模糊的大问题变成清爽的任务列表
task_decomposer_agent = Agent(
    get_model(),
    output_type=DecomposedTasks,
    system_prompt=(
        "你是一个任务分解专家。你的职责是将用户复杂的调研需求分解为多个独立、具体且可并行执行的研究子任务。"
        "每个子任务应该专注于一个特定的子领域，确保覆盖用户需求的所有核心点。"
    )
)


# 2. 研究Agent - 职责：针对子任务进行深度挖掘
research_agent = Agent(
    get_model(),
    output_type=ResearchFinding,
    system_prompt=(
        "你是一个深度的研究专家。你需要根据提供的主题 and 描述进行深入分析。"
        "你需要提供具体的关键发现点，并列出可能的信息来源（真实或模拟行业权威来源）。"
    )
)


# 3. 报告整合Agent - 职责：将零散的研究点串成一篇有灵魂的报告
report_integrator_agent = Agent(
    get_model(),
    output_type=ResearchReport,
    system_prompt=(
        "你是一个高级分析师和报告专家。你的任务是收集来自不同领域的专业研究发现，"
        "并将它们合成为一份结构清晰、逻辑严密、专业性强的研究报告。"
        "报告需要包含吸引人的标题、精炼的执行摘要、详细的研究发现总结以及切实可行的建议。"
    )
)


# ==================== Director Agent 协调逻辑 ====================
# 【教练笔记】：这是整个系统的“大脑”，负责指挥 Agent 们接力工作。

class MultiAgentOrchestrator:
    """多Agent协作编排器"""
    
    def __init__(self):
        self.task_decomposer = task_decomposer_agent
        self.researcher = research_agent
        self.report_integrator = report_integrator_agent
    
    async def orchestrate_research(self, research_request: str) -> ResearchReport:
        """协调多个Agent完成研究任务：三阶段接力"""
        
        # 使用 f-string 进行优雅的字符串格式化
        print(f"🔍 开始多Agent协作研究任务: {research_request.strip()[:50]}...")
        
        # --- 阶段1: 任务分解 ---
        # 目标：明确我们要研究哪些具体方向
        print("📋 阶段1 - 任务分解")
        decomposed_result = await self.task_decomposer.run(
            f"请将以下研究需求分解为具体的研究主题: {research_request}"
        )
        
        # 获取结构化的输出结果
        research_topics = decomposed_result.output.topics
        print(f"📊 分解出 {len(research_topics)} 个研究主题:")
        for t in research_topics:
            print(f"  - {t.name}: {t.description}")
        
        # --- 阶段2: 并行研究 (多箭齐发) ---
        # 【教练笔记】：这里体现了并发的威力。
        # 我们不是一个接一个做研究，而是让多个 Agent 同时开工。
        print("\n🔬 阶段2 - 并行研究")
        research_tasks = []
        for topic in research_topics:
            # 准备任务列表，此时任务还没真正开始执行
            task = self.researcher.run(f"请针对以下主题进行深入研究: {topic.name} (描述: {topic.description})")
            research_tasks.append(task)
        
        # asyncio.gather 就像发令枪，让所有任务同时起跑
        # 结果会按任务列表的顺序返回
        research_results = await asyncio.gather(*research_tasks)
        
        # 提取每个研究 Agent 的结构化结果
        findings = [r.output for r in research_results]
        
        print(f"✅ 完成 {len(findings)} 个主题研究")
        
        # --- 阶段3: 报告整合 ---
        # 目标：将碎片化的信息聚合成结构化的深度报告
        print("\n" + "="*40)
        print("📝 阶段3 - 报告整合")
        print("="*40)
        print("正在将所有研究发现合成最终报告，这可能需要一点时间...")
        
        # 将研究发现转化为文本上下文，传递给整合 Agent
        findings_context = "\n\n".join([
            f"--- 研究发现: {f.topic} ---\n"
            f"关键点: {', '.join(f.key_points)}\n"
            f"参考来源: {', '.join(f.sources)}"
            for f in findings
        ])
        
        report_result = await self.report_integrator.run(
            f"基于以下由专业研究 Agent 提供的详细研究发现，生成一份完整且结构化的研究报告:\n\n{findings_context}"
        )
        
        print("\n🎉 多Agent协作任务完成!")
        return report_result.output


# ==================== 使用示例 ====================

async def main():
    """多Agent协作示例运行入口"""
    
    orchestrator = MultiAgentOrchestrator()
    
    # 复杂的研究请求：可以随意更换，Agent 会自动分解
    research_request = """
    中国核聚变发电目前的研究进展和对未来发展的预测。
    """
    
    try:
        # 使用 await 进行异步调用，就像在接力赛中等待接棒
        report = await orchestrator.orchestrate_research(research_request)
        
        # 打印最终生成的精美报告
        print("\n" + "="*80)
        print(f"📊 报告标题: {report.title}")
        print("="*80)
        print(f"\n【执行摘要】\n{report.executive_summary}")
        
        print(f"\n【详细研究发现】")
        for i, finding in enumerate(report.findings, 1):
            print(f"\n{i}. 主题: {finding.topic}")
            for point in finding.key_points:
                print(f"   - {point}")
            print(f"   来源: {', '.join(finding.sources)}")
            
        print(f"\n【战略建议】")
        for i, rec in enumerate(report.recommendations, 1):
            print(f" - {rec}")
            
        print("\n" + "="*80)
        
    except Exception as e:
        print(f"❌ 协作过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


# 【Python 小白贴士汇总】：
# 1. async/await: 就像接力棒。async 函数会等待（await）耗时任务（如AI回复）完成后再继续。
# 2. 类型提示 (List[str]): 帮助你清楚地知道变量里装的是什么。
# 3. f-string: 优雅地在句子中插入变量。
# 4. asyncio.gather: 并发神器，让多个 AI 同时为你工作。

if __name__ == "__main__":
    asyncio.run(main())
