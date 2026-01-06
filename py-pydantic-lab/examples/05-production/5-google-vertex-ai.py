"""
示例 05-production/5-google-vertex-ai.py: Google Vertex AI (Gemini) 企业级集成

核心价值：Google Cloud 生态集成
在企业级场景中，通常通过 Google Cloud Vertex AI 使用 Gemini 模型。
与直接使用 Google AI Studio (API Key) 不同，Vertex AI 提供了：
1. 企业级安全与合规性。
2. 基于 IAM (Identity and Access Management) 的精细权限控制。
3. 可预测的配额管理和 SLA。

本示例演示如何配置 PydanticAI 以通过 Project ID 和 Location 调用 Vertex AI 上的 Gemini 服务。
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import Optional

# 尝试导入 Google Cloud 相关库
try:
    from google.auth import default
    from pydantic_ai.models.google import GoogleModel
    from pydantic_ai.providers.google import GoogleProvider
except ImportError:
    print("❌ 缺少必要库。请运行: pip install google-auth pydantic-ai")
    sys.exit(1)

from pydantic_ai import Agent

# 环境配置：将 common 目录加入路径以复用 models.py
root = Path(__file__).resolve().parents[1]
sys.path.append(str(root))
from common.models import get_model, LLMProvider

def setup_vertex_ai_model(
    model_name: Optional[str] = None,
    project_id: Optional[str] = None,
    location: Optional[str] = None
) -> GoogleModel:
    """
    配置基于 Vertex AI 的 Google Gemini 模型实例
    
    设计模式：工厂模式
    """
    # 优先从参数获取，否则从环境变量获取
    project = project_id or os.getenv('GOOGLE_PROJECT_ID')
    loc = location or os.getenv('GOOGLE_LOCATION', 'us-central1')
    model = model_name or os.getenv('GOOGLE_MODEL_NAME', 'gemini-1.5-pro')
    
    if not project:
        raise ValueError("GOOGLE_PROJECT_ID 未设置。请在环境变量中设置或作为参数传入。")

    print(f"🛠️  初始化 GoogleModel: {model}")
    print(f"📍 Location: {loc}")
    print(f"🏢 Project: {project}")

    # 初始化 Provider
    # vertexai=True 标志指示使用 Vertex AI 端点而非 Google AI Studio
    provider = GoogleProvider(
        vertexai=True,
        project=project,
        location=loc
    )

    return GoogleModel(model, provider=provider)

async def main():
    print("--- 示例: Google Vertex AI (Gemini) 集成 ---")
    
    # 获取配置
    project_id = os.getenv("GOOGLE_PROJECT_ID")
    
    if not project_id:
        print("⚠️ 未检测到 GOOGLE_PROJECT_ID。")
        print("请在 .env 中设置该变量，或确保你的环境已配置 Application Default Credentials (ADC)。")
        print("\n可以使用以下命令配置本地认证：")
        print("gcloud auth application-default login")
        print("\n本示例将展示如何通过 get_model() 工厂方法进行集成。")
        return

    # 方式 1: 使用自定义设置函数
    print("\n[方式 1] 使用专用设置函数:")
    try:
        model = setup_vertex_ai_model()
        agent = Agent(model, system_prompt="你是一个 Google Cloud 专家。")
        
        print("🚀 正在连接到 Vertex AI...")
        # 注意：这里可能因为缺少真实凭证而失败，所以我们包裹在 try-except 中
        result = await agent.run("简述 Vertex AI 相比于 AI Studio 的优势。")
        print("\n--- Agent 回复 ---")
        print(result.data)
    except Exception as e:
        print(f"\n❌ 调用失败: {str(e)}")

    # 方式 2: 使用通用的 get_model 工厂 (推荐在应用中使用)
    print("\n[方式 2] 使用统一工厂方法 (get_model):")
    try:
        # 设置环境变量以模拟切换
        os.environ['LLM_PROVIDER'] = LLMProvider.GEMINI_VERTEX.value
        factory_model = get_model()
        print(f"✅ 成功从工厂获取模型实例: {type(factory_model).__name__}")
        
        # 验证是否为 GoogleModel
        if isinstance(factory_model, GoogleModel):
            print(f"✅ 验证成功：模型类型为 GoogleModel")
        
    except Exception as e:
        print(f"❌ 工厂获取失败: {str(e)}")

    # 🏗️ 【架构师笔记：Google Cloud 设计模式】
    print("\n" + "="*60)
    print("🏗️  架构设计要点：")
    print("1. 基础设施即代码 (IaC)：Project ID 和 Location 应通过环境变量或配置中心管理。")
    print("2. 统一抽象：通过 common.models 中的工厂方法，可以在不同云厂商之间无缝切换。")
    print("3. 认证解耦：使用 GoogleProvider，它能自动处理 ADC (Application Default Credentials)，")
    print("   这意味着同一套代码在本地开发 (gcloud login) 和 GKE/Cloud Run (Managed Service Account) 运行时无需修改。")
    print("4. 区域化部署：通过 Location 参数，可以确保数据处理留在特定地理区域，满足合规要求。")

if __name__ == "__main__":
    asyncio.run(main())
