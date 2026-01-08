# -*- coding: utf-8 -*-
"""
PTC SQL Helper Tool

这是一个基于 PTC (Programmatic Tool Composition) 范式的 SQL Helper 工具。
它直接调用 base_tools 中的 SQLHelperTool。
"""

from data_retrieval.tools.ptc_tools.sql_helper.sql_helper import SQLHelper

__all__ = ["SQLHelper"]

