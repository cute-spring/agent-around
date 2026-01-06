"""
示例 8: 视觉提取与结构化输出 (Vision Extraction & Structured Output)

核心价值：从非结构化图像中提取精准数据 (Precision Extraction)
本示例展示了如何使用 Pydantic AI 将图像中的财务报表（Apple 财报截图）
直接转换为强类型的 Python 对象。
"""

import sys
import os
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field
from pydantic_ai import Agent, BinaryContent

# 将 examples 目录添加到 sys.path 以允许从 common 导入
examples_root = Path(__file__).resolve().parents[1]
if str(examples_root) not in sys.path:
    sys.path.append(str(examples_root))

from common.models import get_model

# 1. 定义财报数据的结构 (Schema)
class OperatingSegment(BaseModel):
    segment_name: str = Field(description="业务板块名称 (例如: Americas, Europe, Japan, Greater China, Rest of Asia Pacific)")
    revenue: str = Field(description="该板块的营收数值 (带单位)")

class AppleReport(BaseModel):
    company_name: str = Field(default="Apple Inc.")
    fiscal_year: int = Field(description="提取数据所属的财年")
    segments: List[OperatingSegment] = Field(
        description="业务板块细分数据，必须包含: Americas, Europe, Japan, Asia Pacific, Retail, Total"
    )
    currency: str = Field(default="USD", description="货币单位")
    summary: str = Field(description="对该财年表现的简短解读")

# 2. 初始化 Agent
def get_agent(use_structured: bool = True):
    if use_structured:
        return Agent(
            get_model(),
            output_type=AppleReport,
            system_prompt=(
                "你是一个精准的财务数据提取助手。请从 Apple 财报图像中提取指定年份的业务板块 (Operating Segments) 数据。"
                "必须提取以下板块: Americas, Europe, Japan, Asia Pacific, Retail 以及 Total Operating Segments。"
            )
        )
    else:
        return Agent(
            get_model(),
            system_prompt="你是一个专业的财务分析师。请分析 Apple 财报图，列出各业务板块（Americas, Europe, Japan, Asia Pacific, Retail）的营收数据。"
        )

def main():
    target_year = 2024
    print(f'--- 示例 8: 业务板块提取 (目标年份: {target_year}) ---')

    project_root = Path(__file__).resolve().parents[3]
    image_path = project_root / 'js-ai-lab' / 'assets' / 'apple-inc-report.png'

    if not image_path.exists():
        print(f"错误: 找不到图片文件 {image_path}")
        return

    image_data = image_path.read_bytes()
    media_type = 'image/png'

    try:
        print(f"正在分析 {target_year} 年数据 (尝试结构化提取)...")
        agent = get_agent(use_structured=True)
        result = agent.run_sync(
            [
                f"请从这张财报中提取 {target_year} 财年的 Operating Segments 数据。",
                BinaryContent(data=image_data, media_type=media_type)
            ]
        )
        json_output = result.output.model_dump_json(indent=2)
        print("\n--- 提取的 JSON 数据 ---")
        print(json_output)

    except Exception as e:
        print(f"\n⚠️ 结构化提取不可用 ({e})，正在回退到纯文本模式...")
        agent = get_agent(use_structured=False)
        result = agent.run_sync(
            [
                f"请分析这张财报中 {target_year} 财年的 Operating Segments 数据（Americas, Europe, Japan, Asia Pacific, Retail, Total）。",
                BinaryContent(data=image_data, media_type=media_type)
            ]
        )
        print("\n--- AI 文本分析结果 ---")
        print(result.output)
        
        # 架构师笔记：
        # 1. 字段映射：通过 Pydantic Field 描述，AI 知道如何将图片中的 "Greater China" 或 "Rest of Asia Pacific" 映射到我们的模型中。
        # 2. 确定性：JSON 输出消除了文本解析的模糊性，适合下游系统直接集成。

    except Exception as e:
        print(f"\n❌ 提取失败: {e}")
        print("\n提示: ")
        print("1. 结构化提取需要模型支持 'Tool Calling'。")
        print("2. 如果你正在使用 Ollama 的 llama3.2-vision，它目前不支持此功能。")
        print("3. 建议尝试使用 GPT-4o 或其他支持工具调用的多模态模型。")

if __name__ == '__main__':
    main()
