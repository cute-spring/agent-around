"""
示例 05-production/4-azure-ad-auth.py: Azure AD OAuth2 身份验证 (Managed Identity & Client Secret)

核心价值：企业级安全性
在生产环境中，硬编码 API Key 是高风险行为。
Azure OpenAI 支持通过 Azure Active Directory (AAD) 进行身份验证。
本示例演示如何使用 PydanticAI 结合 Managed Identity (托管身份) 或 Client Secret (客户端密码) 进行认证。
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import Optional

# 尝试导入 Azure 相关库
try:
    from azure.identity import DefaultAzureCredential, get_bearer_token_provider
    from openai import AsyncAzureOpenAI
except ImportError:
    print("❌ 缺少必要库。请运行: pip install azure-identity openai")
    sys.exit(1)

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.azure import AzureProvider

# 环境配置
root = Path(__file__).resolve().parents[1]
sys.path.append(str(root))

def setup_azure_ad_model(
    model_name: str = "gpt-4o",
    use_managed_identity: bool = True
) -> OpenAIChatModel:
    """
    配置基于 Azure AD 认证的模型实例
    
    设计模式：工厂模式 + 依赖注入
    """
    
    # 1. 创建 Token Provider
    # 对于 Managed Identity，DefaultAzureCredential 会自动尝试从环境、CLI 或 MSI 获取凭据
    # 对于 Client Secret，需要设置环境变量: AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID
    credential = DefaultAzureCredential()
    
    # Azure OpenAI 的权限范围是固定的
    token_provider = get_bearer_token_provider(
        credential, 
        "https://cognitiveservices.azure.com/.default"
    )

    # 2. 初始化预配置的底层 AsyncAzureOpenAI 客户端
    # 这种方式让 PydanticAI 能够复用底层 SDK 的所有高级认证特性
    az_client = AsyncAzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", "https://your-resource.openai.azure.com/"),
        azure_ad_token_provider=token_provider,
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")
    )

    # 3. 依赖注入：将自定义客户端注入到 PydanticAI 的 Provider 中
    return OpenAIChatModel(
        model_name,
        provider=AzureProvider(openai_client=az_client)
    )

async def main():
    print("--- 示例: Azure AD OAuth2 身份验证 ---")
    
    # 注意：运行此示例需要配置好 Azure 环境
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    if not endpoint or "your-resource" in endpoint:
        print("⚠️ 未检测到有效的 AZURE_OPENAI_ENDPOINT。")
        print("请在 .env 中设置该变量，或确保你的环境已配置 Managed Identity。")
        print("本示例仅展示架构实现代码。")
        return

    # 初始化 Agent
    model = setup_azure_ad_model()
    agent = Agent(model, system_prompt="你是一个安全审计专家。")

    print(f"🚀 正在通过 Azure AD 认证连接到: {endpoint}")
    
    try:
        result = await agent.run("简述为什么使用 Managed Identity 比 API Key 更安全。")
        print("\n--- Agent 回复 ---")
        print(result.data)
    except Exception as e:
        print(f"\n❌ 认证或调用失败: {str(e)}")
        print("提示：请检查你的账户是否已被授予 'Cognitive Services OpenAI User' 角色。")

    # 🏗️ 【架构师笔记：身份认证的最佳实践】
    print("\n" + "="*60)
    print("🏗️  架构设计要点：")
    print("1. 零信任架构 (Zero Trust)：不再依赖静态 API Key，而是基于动态 Token。")
    print("2. 权限最小化 (PoLP)：通过 Azure RBAC 为 Agent 分配特定的资源访问角色。")
    print("3. 凭据轮换 (Rotation)：OAuth2 Token 自动刷新，无需人工干预。")
    print("4. 环境感知 (Environment Awareness)：DefaultAzureCredential 允许同一份代码在本地(CLI登录)和云端(MSI)无缝切换。")

if __name__ == "__main__":
    asyncio.run(main())
