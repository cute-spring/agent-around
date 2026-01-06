"""
示例 9: 多维财务审计专家 (Multi-Dimensional Financial Auditor)

核心价值：复杂表格的视觉推理与交叉校验
本示例不仅提取数据，还要求 AI 像审计师一样：
1. 同时解析“区域 (Segments)”和“产品 (Products)”两个维度的表格。
2. 提取 Q1 2010 的关键指标 (Units, Revenue)。
3. 识别出同比 (YoY) 增长最快的“明星产品”。
"""

import sys
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field
from pydantic_ai import Agent, BinaryContent

# 环境设置
examples_root = Path(__file__).resolve().parents[1]
if str(examples_root) not in sys.path:
    sys.path.append(str(examples_root))

from common.models import get_model

# --- 1. 定义多维数据模型 ---

class DataRow(BaseModel):
    name: str = Field(description="行名称 (如 Americas 或 iPhone)")
    units_k: Optional[str] = Field(None, description="销量 (Units K)")
    revenue_m: str = Field(description="营收 (Revenue $M)")
    yoy_growth_revenue: str = Field(description="营收同比增长率 (Year/Year Change Revenue)")

class AuditReport(BaseModel):
    report_title: str = Field(default="Apple Q1 2010 Summary")
    
    # 维度一：地理区域细分
    regional_segments: List[DataRow] = Field(description="Operating Segments 表格数据")
    
    # 维度二：产品线细分
    product_summary: List[DataRow] = Field(description="Product Summary 表格数据")
    
    # 财务摘要与洞察
    total_revenue_q1_2010: str = Field(description="Q1 2010 总营收")
    star_performer: str = Field(description="本次财报中表现最突出的产品或区域及其原因")
    data_consistency_check: bool = Field(description="验证各区域营收总和是否与 Total 匹配")

# --- 2. 初始化审计 Agent ---

def get_agent(use_structured: bool = True):
    """
    根据模型能力动态创建 Agent。
    如果模型不支持 Tool Calling (如 llama3.2-vision), 则使用非结构化模式。
    """
    if use_structured:
        return Agent(
            get_model(),
            output_type=AuditReport,
            system_prompt=(
                "你是一个资深的财务审计 Agent。你需要从 Apple 的汇总数据图中提取 Q1 2010 的数据。"
                "注意：图中包含多列（Q4 09, Q1 09, Q1 10），你必须只提取 Q1 2010 这一列的数据。"
                "请将结果以结构化 JSON 格式返回。"
            )
        )
    else:
        return Agent(
            get_model(),
            system_prompt=(
                "你是一个资深的财务审计 Agent。请分析 Apple 财报图，提取 Q1 2010 的数据。"
                "请列出主要的区域营收、产品销量和营收，并指出表现最突出的产品。"
            )
        )

def main():
    print('--- 示例 9: 多维财务审计演示 (Apple Q1 2010) ---')

    # 指向您提供的图片
    project_root = Path(__file__).resolve().parents[3]
    image_path = project_root / 'js-ai-lab' / 'assets' / 'apple-inc-report.png'

    if not image_path.exists():
        print(f"提示: 请确保图片已放置在 {image_path}")
        return

    image_data = image_path.read_bytes()

    # 尝试首先使用结构化模式，如果失败则回退
    try:
        print("🔍 正在启动多维审计分析 (尝试结构化提取)...")
        agent = get_agent(use_structured=True)
        result = agent.run_sync(
            [
                "请分析这份 Q1 2010 财报截图，提取区域和产品数据，并找出增长最快的引擎。",
                BinaryContent(data=image_data, media_type='image/png')
            ]
        )
        report = result.output
        display_report(report)

    except Exception as e:
        print(f"\n⚠️ 结构化提取挑战: {e}")
        print("正在回退到纯文本审计模式以获取洞察...\n")
        
        fallback_agent = get_agent(use_structured=False)
        result = fallback_agent.run_sync(
            [
                "请深入分析这份 Q1 2010 财报截图。提取主要数据，并特别指出营收增长最快的产品或区域。",
                BinaryContent(data=image_data, media_type='image/png')
            ]
        )
        print("--- 财务审计报告 (文本分析) ---")
        print(result.output)

def display_report(report: AuditReport):
    # --- 3. 结构化展示结果 ---
    print(f"\n📊 报告标题: {report.report_title}")
    print(f"💰 Q1 2010 总营收: {report.total_revenue_q1_2010}")
    
    print("\n📍 区域表现 (Regional Segments):")
    for seg in report.regional_segments:
        print(f"  - {seg.name:15} | 营收: {seg.revenue_m:8} | YoY: {seg.yoy_growth_revenue}")

    print("\n📱 产品表现 (Product Summary):")
    for prod in report.product_summary:
        units = f"{prod.units_k}K" if prod.units_k else "N/A"
        print(f"  - {prod.name:15} | 销量: {units:8} | 营收: {prod.revenue_m:8} | YoY: {prod.yoy_growth_revenue}")

    print("\n💡 审计洞察:")
    print(report.star_performer)
    
    print(f"\n✅ 数据一致性校验: {'通过' if report.data_consistency_check else '待核实'}")

if __name__ == '__main__':
    main()
