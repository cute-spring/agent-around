"""
多Agent协作编排示例

展示如何使用Director Agent协调多个专业Worker Agent完成复杂任务
"""

import asyncio
from typing import List, Optional
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from examples.common.models import get_model


# ==================== 领域模型定义 ====================

class ResearchTopic(BaseModel):
    """研究主题"""
    name: str = Field(description="主题名称")
    description: str = Field(description="主题描述")


class ResearchFinding(BaseModel):
    """研究发现"""
    topic: str = Field(description="研究主题")
    key_points: List[str] = Field(description="关键发现点")
    sources: List[str] = Field(description="信息来源")


class ResearchReport(BaseModel):
    """研究报告"""
    title: str = Field(description="报告标题")
    executive_summary: str = Field(description="执行摘要")
    findings: List[ResearchFinding] = Field(description="研究发现列表")
    recommendations: List[str] = Field(description="建议措施")


# ==================== 专业Agent定义 ====================

# 1. 任务分解Agent - 负责将复杂任务拆解为子任务
task_decomposer_agent = Agent(
    model=get_model(),
    system_prompt="""你是一个专业的任务分解专家。负责将复杂的业务需求拆解为具体的可执行子任务。
请分析用户需求，输出一个结构化的研究主题列表。"""
)


# 2. 研究Agent - 负责深入研究每个子主题
research_agent = Agent(
    model=get_model(),
    result_type=ResearchFinding,
    system_prompt="""你是一个专业的研究员。基于给定的研究主题，进行深入调研并输出结构化发现。
请确保发现点有事实依据，并注明信息来源。"""
)


# 3. 报告整合Agent - 负责将多个研究发现整合为完整报告
report_integrator_agent = Agent(
    model=get_model(),
    result_type=ResearchReport,
    system_prompt="""你是一个专业的报告撰写专家。负责将多个研究发现整合为结构化的研究报告。
请生成专业的执行摘要和 actionable 的建议措施。"""
)


# ==================== Director Agent 协调逻辑 ====================

class MultiAgentOrchestrator:
    """多Agent协作编排器"""
    
    def __init__(self):
        self.task_decomposer = task_decomposer_agent
        self.researcher = research_agent
        self.report_integrator = report_integrator_agent
    
    async def orchestrate_research(self, research_request: str) -> ResearchReport:
        """协调多个Agent完成研究任务"""
        
        print("🔍 开始多Agent协作研究任务...")
        
        # 阶段1: 任务分解
        print("📋 阶段1 - 任务分解")
        topics_result = await self.task_decomposer.run(
            f"请将以下研究需求分解为具体的研究主题: {research_request}"
        )
        
        # 解析研究主题 (这里简化处理，实际应该用更复杂的解析逻辑)
        research_topics = [
            "人工智能在医疗诊断中的应用",
            "机器学习在药物发现中的进展", 
            "自然语言处理在电子病历分析中的使用"
        ]
        
        print(f"📊 分解出 {len(research_topics)} 个研究主题")
        
        # 阶段2: 并行研究
        print("🔬 阶段2 - 并行研究")
        research_tasks = []
        for topic in research_topics:
            task = self.researcher.run(f"请深入研究: {topic}")
            research_tasks.append(task)
        
        findings = await asyncio.gather(*research_tasks)
        
        print(f"✅ 完成 {len(findings)} 个主题研究")
        
        # 阶段3: 报告整合
        print("📝 阶段3 - 报告整合")
        findings_text = "\n".join([
            f"主题: {f.topic}\n关键点: {', '.join(f.key_points[:2])}"
            for f in findings
        ])
        
        report = await self.report_integrator.run(
            f"基于以下研究发现，生成完整的研究报告:\n{findings_text}"
        )
        
        print("🎉 多Agent协作任务完成!")
        return report


# ==================== 使用示例 ====================

async def main():
    """多Agent协作示例"""
    
    orchestrator = MultiAgentOrchestrator()
    
    # 复杂的研究请求
    research_request = """
    请调研人工智能在医疗健康领域的最新应用进展，
    重点关注诊断辅助、药物发现和病历分析三个方向，
    并给出具体的技术实现方案和商业应用建议。
    """
    
    try:
        report = await orchestrator.orchestrate_research(research_request)
        
        print("\n" + "="*60)
        print("📄 最终研究报告")
        print("="*60)
        print(f"标题: {report.title}")
        print(f"\n摘要: {report.executive_summary}")
        print(f"\n研究发现数量: {len(report.findings)}")
        print(f"\n建议措施: {', '.join(report.recommendations[:3])}...")
        
    except Exception as e:
        print(f"❌ 协作过程中出现错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())