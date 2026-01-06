"""
示例 10: 动态时期数据提取器 (Dynamic Period Extractor)

核心价值：根据动态输入的时期（Q4 2009, Q1 2010 等），在复杂多列报表中精准定位并提取数据。
"""

import sys
import os
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field
from pydantic_ai import Agent, BinaryContent

# 环境设置
examples_root = Path(__file__).resolve().parents[1]
if str(examples_root) not in sys.path:
    sys.path.append(str(examples_root))

from common.models import get_model

# --- 1. 定义数据结构 ---

class SegmentData(BaseModel):
    operatingSegments: str = Field(description="业务板块名称 (如 Americas, Europe)")
    cpu: str = Field(description="该时期的 Units K (销量)")
    revenue: str = Field(description="该时期的 Revenue $M (营收)")

class PeriodReport(BaseModel):
    period: str = Field(description="所提取数据的时期 (如 Q4 2009)")
    data: List[SegmentData] = Field(description="该时期的业务细分数据列表")

# --- 2. 初始化动态 Agent ---

def get_extraction_agent():
    return Agent(
        get_model(),
        output_type=List[SegmentData], # 使用 output_type
        system_prompt=(
            "你是一个精准的数据提取专家。用户会提供一个财报图片和一个目标时期（如 Q4 2009）。"
            "图片中的表格包含多列数据：'Q4 09', 'Q1 09', 'Q1 10'。"
            "你的任务是：\n"
            "1. 在 'Operating Segments' 表格中找到匹配用户请求时期的那一列。\n"
            "2. 提取该列中每个区域（Americas, Europe, Japan, Asia Pacific, Retail）的 Units 和 Revenue。\n"
            "3. 注意：Units 对应输出中的 'cpu' 字段，Revenue 对应 'revenue' 字段。\n"
            "4. 只返回数据，不要包含任何解释。"
        )
    )

def run_extraction(period: str):
    print(f"\n🔍 正在尝试提取时期: {period} 的数据...")
    
    project_root = Path(__file__).resolve().parents[3]
    image_path = project_root / 'js-ai-lab' / 'assets' / 'apple-inc-report.png'
    image_data = image_path.read_bytes()

    agent = get_extraction_agent()
    
    try:
        result = agent.run_sync(
            [
                f"请从图片中提取 {period} 的 Operating Segments 数据。",
                BinaryContent(data=image_data, media_type='image/png')
            ]
        )
        
        print(f"✅ 成功提取 {period} 数据:")
        for item in result.output: # 使用 output 而不是 data
            print(f"   - {item.operatingSegments:15} | CPU: {item.cpu:6} | Revenue: {item.revenue}")
            
    except Exception as e:
        print(f"❌ 提取失败: {e}")

if __name__ == "__main__":
    print('--- 示例 10: 动态时期提取演示 ---')
    
    # 测试不同的时期输入
    periods_to_test = ["Q4 2009", "Q1 2010"]
    
    for p in periods_to_test:
        run_extraction(p)
