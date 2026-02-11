# -*- coding: utf-8 -*-
"""
Central tool registry for data-retrieval.

Why:
- FastAPI tool server and MCP server should share the same tool mapping.
- Avoid duplicating tool lists in multiple entrypoints.
"""

from __future__ import annotations

from typing import Dict, Type

# Base tools
from data_retrieval.tools.base_tools.json2plot import Json2Plot
from data_retrieval.tools.base_tools.text2sql import Text2SQLTool
from data_retrieval.tools.base_tools.text2metric import Text2Metric
from data_retrieval.tools.base_tools.sql_helper import SQLHelperTool
from data_retrieval.tools.base_tools.knowledge_item import KnowledgeItemTool
from data_retrieval.tools.base_tools.get_metadata import GetMetadataTool
from data_retrieval.tools.base_tools.get_tool_cache import GetToolCacheTool

# Sandbox tools (dict mappings)
from data_retrieval.tools.sandbox_tools.toolkit import SANDBOX_TOOLS_MAPPING
from data_retrieval.tools.sandbox_tools_new import SANDBOX_TOOLS_NEW_MAPPING


# NOTE: keep keys stable; they are part of API contracts (FastAPI, future MCP).
BASE_TOOLS_MAPPING: Dict[str, Type] = {
    "text2sql": Text2SQLTool,
    "text2metric": Text2Metric,
    "sql_helper": SQLHelperTool,
    "knowledge_item": KnowledgeItemTool,
    "get_metadata": GetMetadataTool,
    "json2plot": Json2Plot,
    # "get_tool_cache": GetToolCacheTool,
}

# 为旧沙箱工具添加 _legacy 后缀
SANDBOX_LEGACY_TOOLS: Dict[str, Type] = {
    f"{k}_legacy": v for k, v in SANDBOX_TOOLS_MAPPING.items()
}

ALL_TOOLS_MAPPING: Dict[str, Type] = (
    BASE_TOOLS_MAPPING
    | SANDBOX_TOOLS_NEW_MAPPING  # 新沙箱工具直接使用原名
    | SANDBOX_LEGACY_TOOLS  # Legacy 工具排在最后
)
