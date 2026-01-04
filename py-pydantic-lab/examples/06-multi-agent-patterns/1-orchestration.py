"""
模式 A (升级版)：编排模式 (Orchestration with Error Handling)

提升点：
1. 鲁棒并行处理：使用 asyncio.gather 并设置 return_exceptions=True，确保个别子任务失败不会拖垮全局。
2. 动态结果过滤：自动剔除失败的子研究任务，仅将成功的部分交给整合者。
3. 结构化日志：清晰展示每个子任务的状态。
"""
import asyncio
import sys
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field
from pydantic_ai import Agent

# 环境配置
root = Path(__file__).resolve().parents[1]
sys.path.append(str(root))
from common.models import get_model

# 1. 模型定义
class Task(BaseModel):
    name: str
    desc: str

class DecomposedTasks(BaseModel):
    tasks: List[Task]

class SubResult(BaseModel):
    topic: str
    content: str

# 2. Agent 定义
decomposer = Agent(get_model(), output_type=DecomposedTasks, system_prompt="将需求拆解为2-3个子任务")
researcher = Agent(get_model(), output_type=SubResult, system_prompt="深入研究子任务并给出结论")
integrator = Agent(get_model(), system_prompt="将多个子研究结论整合成一篇简报")

# 3. 编排逻辑 (Orchestrator)
async def run_orchestration(request: str):
    print(f"🚀 [编排模式-升级版] 开始处理: {request}")
    
    # --- 步骤 1: 拆解 ---
    try:
        plan = await decomposer.run(request)
        tasks = plan.output.tasks
    except Exception as e:
        print(f"❌ 任务拆解失败: {e}")
        return
    
    # --- 步骤 2: 研究 (并行 + 容错) ---
    # 【教练笔记】：这是“编排模式”。
# 它的哲学类似于 [MetaGPT](https://github.com/geekan/MetaGPT) 的 SOP (标准作业程序)。
# 在 MetaGPT 中，任务被拆解为多个明确的步骤，由不同的角色（如程序员、架构师）按顺序执行。
# 我们这里通过 Python 的 asyncio.gather 实现了并行的 SOP。
    # return_exceptions=True 允许我们捕获每个任务的独立结果。
    print(f"📊 正在处理 {len(tasks)} 个并行子任务...")
    jobs = [researcher.run(f"主题: {t.name}, 要求: {t.desc}") for t in tasks]
    
    results = await asyncio.gather(*jobs, return_exceptions=True)
    
    successful_findings = []
    for i, res in enumerate(results):
        if isinstance(res, Exception):
            print(f"⚠️ 子任务 [{tasks[i].name}] 执行失败，已跳过。错误: {res}")
        else:
            print(f"✅ 子任务 [{tasks[i].name}] 完成。")
            successful_findings.append(res.output)
    
    if not successful_findings:
        print("❌ 所有子任务均失败，无法生成报告。")
        return

    # --- 步骤 3: 整合 ---
    print(f"📝 正在根据 {len(successful_findings)} 份成功的研究结果生成报告...")
    context = "\n\n".join([f"主题: {f.topic}\n结论: {f.content}" for f in successful_findings])
    
    try:
        final_report = await integrator.run(f"请整合以下内容: \n{context}")
        print("\n" + "="*50)
        print("🏁 最终简报：")
        print(final_report.output)
        print("="*50)
    except Exception as e:
        print(f"❌ 结果整合失败: {e}")

if __name__ == "__main__":
    asyncio.run(run_orchestration("分析未来5年AR眼镜的技术瓶颈与市场机遇"))
