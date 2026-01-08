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
from data_retrieval.tools.base_tools.text2dip_metric import Text2DIPMetricTool
from data_retrieval.tools.base_tools.sql_helper import SQLHelperTool
from data_retrieval.tools.base_tools.knowledge_item import KnowledgeItemTool
from data_retrieval.tools.base_tools.get_metadata import GetMetadataTool
from data_retrieval.tools.graph_tools.nl2ngql_qq import Text2nGQLTool

# Sandbox + knowledge network tools (dict mappings)
from data_retrieval.tools.sandbox_tools.toolkit import SANDBOX_TOOLS_MAPPING
from data_retrieval.tools.knowledge_network_tools import KNOWLEDGE_NETWORK_TOOLS_MAPPING


# NOTE: keep keys stable; they are part of API contracts (FastAPI, future MCP).
BASE_TOOLS_MAPPING: Dict[str, Type] = {
    "text2sql": Text2SQLTool,
    "text2ngql": Text2nGQLTool,
    "text2metric": Text2DIPMetricTool,
    "sql_helper": SQLHelperTool,
    "knowledge_item": KnowledgeItemTool,
    "get_metadata": GetMetadataTool,
    "json2plot": Json2Plot,
}

ALL_TOOLS_MAPPING: Dict[str, Type] = (
    BASE_TOOLS_MAPPING | SANDBOX_TOOLS_MAPPING | KNOWLEDGE_NETWORK_TOOLS_MAPPING
)


