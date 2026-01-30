from fastapi import APIRouter, HTTPException, Body
from typing import List, Dict, Any
import json
import os
from app.mcp.manager import mcp_manager

router = APIRouter()

CONFIG_PATH = mcp_manager.config_path

@router.get("/")
async def list_configs():
    return mcp_manager.load_config()

@router.post("/")
async def update_configs(configs: List[Dict[str, Any]]):
    try:
        with open(CONFIG_PATH, 'w') as f:
            json.dump(configs, f, indent=2)
        # Note: Changes require server restart to take full effect for now
        return configs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
