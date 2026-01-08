# -*- coding: utf-8 -*-
"""
PTC Text2SQL Tool

这是一个基于 PTC (Programmatic Tool Composition) 范式的 Text2SQL 工具。
它直接调用 base_tools 中的 Text2SQLTool。
配置会自动从 YAML 文件中加载。
"""

from data_retrieval.tools.ptc_tools.text2sql.text2sql import Text2SQL

__all__ = ["Text2SQL"]

