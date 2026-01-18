import os
from pydantic_ai.mcp import MCPServerStdio

def create_mcp_server(config: dict) -> MCPServerStdio:
    """
    根据配置字典创建 MCPServerStdio 实例。
    
    配置格式示例:
    {
        "command": "npx",
        "args": ["-y", "mcp-server-weread"],
        "env_keys": ["WEREAD_COOKIE"]
    }
    """
    command = config.get("command", "npx")
    args = config.get("args", [])
    env_keys = config.get("env_keys", [])
    
    # 基础环境变量
    env = os.environ.copy()
    
    # 检查并确保必要的环境变量存在
    missing_keys = [key for key in env_keys if not env.get(key)]
    if missing_keys:
        # 这里可以选择抛出异常或打印警告
        # 为了演示，我们先打印警告
        print(f"警告: 缺少必要的 MCP 环境变量: {', '.join(missing_keys)}")
        
    return MCPServerStdio(command, args=args, env=env)
