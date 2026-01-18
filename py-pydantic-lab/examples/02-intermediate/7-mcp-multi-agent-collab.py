"""
示例 7: 多 Agent + MCP 协作 (城市文化漫游策划)

核心模式：编排模式 (Orchestration)
在这个例子中，我们构建了一个“深度城市探索团队”，由三个角色组成：
1. Scout Agent (探路者): 负责地理空间信息，通过 AMap MCP 获取实时位置、天气和周边。
2. Librarian Agent (文史馆长): 负责文化深度，通过 WeRead MCP 检索相关书籍和人文背景。
3. Planner Agent (总策划): 负责协调，根据用户需求调度 Scout 和 Librarian，并汇总最终方案。

展示要点：
1. 职责分离：每个 Agent 专注于自己的领域和工具。
2. Agent 嵌套：Planner 将 Scout 和 Librarian 作为“工具”调用。
3. MCP 多路连接：同时管理并连接多个不同的 MCP 服务器。
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext
from pydantic_ai.mcp import MCPServerStdio

# --- 环境准备 ---
env_paths = [
    Path(__file__).resolve().parent / ".env",
    Path(__file__).resolve().parents[2] / ".env",
    Path(__file__).resolve().parents[3] / ".env",
]

for env_path in env_paths:
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        break

examples_root = Path(__file__).resolve().parents[1]
if str(examples_root) not in sys.path:
    sys.path.append(str(examples_root))

from common.models import get_model

# --- 定义角色 Agent ---

# 1. 探路者 Agent (连接高德 MCP)
scout_agent = Agent(
    get_model(),
    name='scout',
    system_prompt=(
        "你是一个精通地理信息的探路者。"
        "你的任务是使用高德地图工具，寻找具体的地点、检查天气或计算路线。"
        "请只提供客观的地理和环境数据。"
    )
)

# 2. 文史馆长 Agent (连接微信读书 MCP)
librarian_agent = Agent(
    get_model(),
    name='librarian',
    system_prompt=(
        "你是一个博学多才的文史馆长。"
        "你的任务是从书籍和历史文献中挖掘地点的文化内涵、历史故事和文学关联。"
        "请为地理位置注入‘灵魂’。"
    )
)

# 3. 总策划 Agent (协调者)
planner_agent = Agent(
    get_model(),
    name='planner',
    system_prompt=(
        "你是一个高端定制旅行策划师。"
        "你的目标是为用户提供一份既有地理便捷性、又有文化深度的城市漫游方案。"
        "你不能直接调用 MCP 工具，但你可以通过调用 'ask_scout' 和 'ask_librarian' 来获取信息。"
        "\n工作流：\n"
        "1. 理解用户需求（如：地点、偏好）。\n"
        "2. 调用 scout 获取位置、天气和具体兴趣点（POI）。\n"
        "3. 调用 librarian 针对这些兴趣点检索相关的文化背景或推荐书籍。\n"
        "4. 汇总一份完美的方案，格式要求：[地理坐标] + [实时状况] + [文化故事] + [漫游建议]。"
    )
)

# --- 定义 Agent 间的协作工具 ---

@planner_agent.tool
async def ask_scout(ctx: RunContext, query: str) -> str:
    """向探路者询问地理、位置、天气等信息。"""
    # 这里我们将 scout_agent 的结果直接返回给 planner
    result = await scout_agent.run(query, usage=ctx.usage)
    return result.output

@planner_agent.tool
async def ask_librarian(ctx: RunContext, query: str) -> str:
    """向文史馆长询问关于地点的历史文化、书籍推荐或背景故事。"""
    result = await librarian_agent.run(query, usage=ctx.usage)
    return result.output

# --- 主逻辑：管理 MCP 生命周期并运行 ---

async def main():
    print('--- 示例 7: 多 Agent + MCP 协作 (深度漫游策划) ---')
    
    # 1. 定义并启动 MCP 服务器
    # 高德地图 MCP
    amap_server = MCPServerStdio(
        'npx',
        args=['-y', '@amap/amap-maps-mcp-server'],
        env=os.environ.copy()
    )
    
    # 微信读书 MCP
    weread_server = MCPServerStdio(
        'npx',
        args=['-y', 'mcp-server-weread'],
        env=os.environ.copy()
    )

    # 将服务器分配给对应的 Agent
    scout_agent.toolsets.append(amap_server)
    librarian_agent.toolsets.append(weread_server)

    # 检查 Key (仅做提醒，即使没有 Key 也可以展示逻辑)
    if not os.getenv('AMAP_MAPS_API_KEY') or not os.getenv('WEREAD_COOKIE'):
        print("\n[注意] 未检测到 AMAP_MAPS_API_KEY 或 WEREAD_COOKIE。")
        print("程序将尝试运行，但 MCP 工具调用可能会失败。")
        print("这没关系，您可以重点观察代码中的多 Agent 协作设计模式。\n")

    # 2. 运行协作流程
    async with amap_server, weread_server:
        # 用户需求
        user_request = "我想在杭州西湖附近安排一个下午的行程，我喜欢南宋历史，希望既能看到漂亮的景色，又能感受到文化底蕴。"
        
        print(f"用户需求: {user_request}\n")
        print("规划师正在调度团队...\n")
        
        try:
            # Planner 启动，它会自动根据需要调用 scout 和 librarian
            result = await planner_agent.run(user_request)
            
            print("\n" + "="*20 + " 最终漫游方案 " + "="*20)
            print(result.output)
            print("="*54)
            
        except Exception as e:
            print(f"\n[运行异常]: {e}")
            print("通常是因为 MCP 服务器在缺少 API Key 的情况下无法正常初始化。")
            print("但在代码层面，您已经看到了如何组织多 Agent 协作。")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
