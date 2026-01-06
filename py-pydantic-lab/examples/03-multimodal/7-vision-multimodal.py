"""
示例 7: 多模态视觉 (Vision / Multimodal)

核心价值：结构化的多模态提取 (Structured Multimodal Extraction)
与 JS 版本相比，Python 版本利用 Pydantic AI 的强项，不仅能分析图片，还能将分析结果
直接映射到 Pydantic 模型中，实现从视觉到结构化数据的无缝转换。
"""

import sys
import os
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field
from pydantic_ai import Agent, BinaryContent

# 将 examples 目录添加到 sys.path 以允许从 common 导入
# py-pydantic-lab/examples/03-multimodal/7-vision-multimodal.py -> parents[1] is examples/
examples_root = Path(__file__).resolve().parents[1]
if str(examples_root) not in sys.path:
    sys.path.append(str(examples_root))

from common.models import get_model, LLMProvider

# 1. 定义输出的结构 (Schema)
class ObjectDetected(BaseModel):
    name: str = Field(description="检测到的物体名称")
    confidence: float = Field(description="置信度 (0.0 到 1.0)")
    description: str = Field(description="对该物体的简短描述")

class ImageAnalysis(BaseModel):
    summary: str = Field(description="对整张图片的简短总结")
    objects: List[ObjectDetected] = Field(description="图片中检测到的主要物体列表")
    dominant_colors: List[str] = Field(description="图片中的主导颜色")
    is_safe: bool = Field(description="图片内容是否安全/合规")

# 2. 初始化 Agent
# 注意：vision 任务通常需要支持多模态的模型，如 gpt-4o, claude-3-5-sonnet 或 llama3.2-vision
# 对于某些不支持 Tool Calling 的模型（如目前的 llama3.2-vision），建议使用非结构化输出。
agent = Agent(
    get_model(),
    # 如果模型支持 Tool Calling，可以使用 output_type=ImageAnalysis 实现结构化提取
    # 但为了兼容性，我们先演示基础的多模态文本返回
    system_prompt="你是一个专业的视觉分析专家。请详细分析用户提供的图片内容。"
)

def main():
    print('--- 示例 7: Pydantic AI 多模态视觉演示 ---')

    # 3. 准备图片路径 (指向共享的 assets 目录)
    # 项目结构中图片位于 js-ai-lab/assets/image-1.png
    project_root = Path(__file__).resolve().parents[3]
    image_path = project_root / 'js-ai-lab' / 'assets' / 'image-1.png'

    if not image_path.exists():
        print(f"错误: 找不到图片文件 {image_path}")
        return

    print(f"正在读取图片: {image_path.name}...")
    
    # 4. 读取图片二进制数据
    image_data = image_path.read_bytes()
    # 简单的扩展名判断 media_type
    media_type = 'image/png' if image_path.suffix.lower() == '.png' else 'image/jpeg'

    try:
        print("正在发送请求到 AI 模型进行分析...")
        
        # 5. 运行 Agent，传入多模态内容
        # pydantic-ai 支持直接在输入列表中混入 BinaryContent
        result = agent.run_sync(
            [
                "这张图片里有什么？请详细描述。",
                BinaryContent(data=image_data, media_type=media_type)
            ]
        )
        
        # 6. 处理结果
        print("\n--- AI 视觉分析结果 ---")
        print(result.output)
        
        # 架构师笔记：
        # 1. 多模态输入：BinaryContent 让图片处理非常直观，无需手动 Base64 编码。
        # 2. 模型限制：某些模型（如 llama3.2-vision）可能不支持 Tool Calling，
        #    这时 Pydantic AI 的结构化提取 (output_type) 会失效，应退回到纯文本模式。
        # 3. 如果需要结构化提取且模型支持，只需添加 output_type=MyModel 即可。
        
        print(f"\nToken 使用情况: {result.usage()}")

    except Exception as e:
        print(f"\n执行失败: {e}")
        print("\n提示: ")
        print("1. 请确保你的 LLM_PROVIDER 支持视觉功能 (推荐使用 OpenAI gpt-4o 或本地 Ollama llama3.2-vision)。")
        print("2. 如果使用 Ollama，请运行: export LLM_PROVIDER=ollama && export OLLAMA_MODEL_NAME=llama3.2-vision")

if __name__ == '__main__':
    main()
