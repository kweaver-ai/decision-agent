# -*- coding: utf-8 -*-
"""
MCP Resources 模块 - 静态资源定义
"""

from typing import List, Dict, Any, Optional
import json

# 静态资源定义
RESOURCES = [
    {
        "uri": "info://service",
        "name": "服务信息",
        "description": "获取 data-retrieval 服务的基本信息",
        "mimeType": "application/json",
    },
]

# 资源模板定义
RESOURCE_TEMPLATES = [
    {
        "uriTemplate": "schema://{identity}",
        "name": "数据源 Schema",
        "description": "获取指定 identity 对应数据源的 schema 信息",
        "mimeType": "application/json",
    },
]


def get_all_resources() -> List[Dict[str, Any]]:
    """获取所有静态资源。"""
    return RESOURCES


def get_all_resource_templates() -> List[Dict[str, Any]]:
    """获取所有资源模板。"""
    return RESOURCE_TEMPLATES


async def read_resource(uri: str) -> Optional[str]:
    """
    读取资源内容。
    
    Args:
        uri: 资源 URI
        
    Returns:
        资源内容（字符串），未找到返回 None
    """
    # 服务信息
    if uri == "info://service":
        from data_retrieval.tools.mcp.registry import list_mcp_tools
        tools = [{"name": t["name"], "description": t.get("description", "")} for t in list_mcp_tools()]
        return json.dumps({
            "name": "data-retrieval",
            "version": "1.0.0",
            "tools": tools,
        }, ensure_ascii=False, indent=2)
    
    # 数据源 Schema
    if uri.startswith("schema://"):
        identity = uri.replace("schema://", "")
        try:
            from data_retrieval.tools.mcp.registry import call_mcp_tool
            result = await call_mcp_tool("get_metadata", {"identity": identity})
            return json.dumps(result, ensure_ascii=False, indent=2) if isinstance(result, (dict, list)) else str(result)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)
    
    return None
