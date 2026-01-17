"""
示例 5: 微信读书 MCP 集成 (Personal Knowledge Management)

核心价值：将 Agent 连接到个人私有数据（如微信读书的笔记、划线），构建“私人图书馆”助手。
功能集成 (mcp-server-weread)：
1. get_bookshelf: 获取用户书架上的所有书籍列表及阅读进度。
2. search_books: 通过关键词在书架中检索特定书籍及其 ID。
3. get_book_notes_and_highlights: 提取指定书籍的划线、笔记，并按章节组织。
4. get_book_best_reviews: 获取书籍的热门书评，用于辅助理解。

架构说明：
1. 使用 Pydantic AI 的 MCPServerStdio 连接到 mcp-server-weread。
2. 展示如何跨越公有知识（LLM 训练数据）与私有知识（用户笔记）进行推理。
3. 演示“语义搜索 -> 笔记提取 -> 主题综述”的典型 PKM 工作流。
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

# 加载环境变量
# 尝试从多个可能的路径加载 .env 文件
env_paths = [
    Path(__file__).resolve().parent / ".env",           # 当前目录
    Path(__file__).resolve().parents[2] / ".env",       # py-pydantic-lab 目录
    Path(__file__).resolve().parents[3] / ".env",       # 项目根目录
]

loaded = False
for env_path in env_paths:
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        print(f"已从 {env_path} 加载环境变量")
        loaded = True
        break

if not loaded:
    # 如果都没找到，尝试默认加载
    load_dotenv()

# 将 examples 目录添加到 sys.path 以允许从 common 导入
examples_root = Path(__file__).resolve().parents[1]
if str(examples_root) not in sys.path:
    sys.path.append(str(examples_root))

from common.models import get_model

async def main():
    print('--- 示例 5: 微信读书 MCP 集成 (私人图书馆助手) ---')
    
    # 1. 检查必要配置
    # mcp-server-weread 需要 WEREAD_COOKIE 或 CookieCloud 配置
    if not os.getenv('WEREAD_COOKIE') and not os.getenv('CC_ID'):
        print("\n[跳过运行] 提示：未检测到 WEREAD_COOKIE。")
        print("请在 .env 中配置微信读书 Cookie 以实际运行此示例。")
        print("您可以从浏览器登录 weread.qq.com 后在控制台获取 Cookie。")
        return

    # 2. 定义 MCP 服务器配置
    # 使用 npx 运行 mcp-server-weread
    # 更多信息: https://github.com/freestylefly/mcp-server-weread
    server = MCPServerStdio(
        'npx',
        args=['-y', 'mcp-server-weread'],
        env=os.environ.copy()
    )
    
    # 3. 初始化 Agent
    agent = Agent(
        get_model(),
        toolsets=[server],
        system_prompt=(
            "你是一个结合了‘数据科学家’、‘心理学家’和‘哲学教练’身份的超级 Agent。"
            "你不仅能管理知识，还能通过用户的阅读行为（书架、笔记、时长、时间维度）挖掘深层的心理和认知模式。"
            "\n你可以进行的深度分析包括：\n"
            "1. **认知迁徙分析**：分析用户在不同时期关注点的变化（例如从‘技术工具’转向‘哲学思考’）。\n"
            "2. **笔记深度建模**：分析用户的笔记是单纯的摘录（Shadowing）还是带有批判性思考（Reflective），并给出反馈。\n"
            "3. **阅读心流推测**：结合阅读时长 and 笔记频率，推测用户在哪些书籍中进入了‘心流’状态。\n"
            "4. **跨学科连通**：发现用户笔记中跨越不同书籍、不同领域的潜在逻辑关联。"
            "\n当用户请求分析时，请灵活组合 'get_bookshelf'、'search_books' 和 'get_book_notes_and_highlights' 等工具。"
            "\n注意：你的语气应该是专业、启发性且充满洞察力的。"
        )
    )
    
    # 4. 运行示例
    async with server:
        # 用户的查询请求
        prompt = "根据我所读的书、做的笔记以及不同时期的阅读数据，你可以做哪些深度的、有趣的分析？请结合我的实际数据（如中医、技术、历史等）给出几个具体的分析方向。"
        print(f"\nPrompt: {prompt}")
        print("正在连接微信读书 MCP 进行深度建模分析...\n")
        
        try:
            result = await agent.run(prompt)
            print("\n=== AI 助手回复 ===")
            print(result.output)
            print("\n====================")
        except Exception as e:
            print(f"\n调用失败: {e}")
            print("提示：请检查您的微信读书 Cookie 是否有效且未过期。")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"程序异常: {e}")
