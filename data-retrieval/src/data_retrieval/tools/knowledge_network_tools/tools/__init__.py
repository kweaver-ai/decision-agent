# -*- coding: utf-8 -*-
"""
工具入口层
统一管理所有API工具入口
"""

# 延迟导入，避免循环依赖
def _get_tools():
    from .retrieval_tool import KnowledgeNetworkRetrievalTool
    from .relation_path_retrieval_tool import RelationPathRetrievalTool
    from .cypher_query_tool import CypherQueryTool
    from .rerank_tool import KnowledgeNetworkRerankTool
    
    return {
        "KnowledgeNetworkRetrievalTool": KnowledgeNetworkRetrievalTool,
        "RelationPathRetrievalTool": RelationPathRetrievalTool,
        "CypherQueryTool": CypherQueryTool,
        "KnowledgeNetworkRerankTool": KnowledgeNetworkRerankTool,
    }

# 动态导出
_tools = None
def __getattr__(name):
    global _tools
    if _tools is None:
        _tools = _get_tools()
    if name in _tools:
        return _tools[name]
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    "KnowledgeNetworkRetrievalTool",
    "RelationPathRetrievalTool",
    "CypherQueryTool",
    "KnowledgeNetworkRerankTool",
]

