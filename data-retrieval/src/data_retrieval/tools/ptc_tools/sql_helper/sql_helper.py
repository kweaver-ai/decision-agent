# -*- coding: utf-8 -*-
# @Author:  Xavier.chen@aishu.cn
# @Date: 2025-01-XX
"""
PTC SQL Helper Tool

这是一个基于 PTC (Programmatic Tool Composition) 范式的 SQL Helper 工具实现。
直接调用 base_tools 中的 SQLHelperTool。
"""

from typing import Optional, Dict, Any

from data_retrieval.logs.logger import logger
from data_retrieval.tools.base_tools.sql_helper import SQLHelperTool, CommandType
from data_retrieval.datasource.dip_dataview import DataView
from data_retrieval.tools.ptc_tools.base import PTCBaseTool


class SQLHelper(PTCBaseTool):
    """PTC SQL Helper Tool
    
    Configuration is automatically loaded from YAML file.
    Default config file paths (in order):
    1. ptc_sql_helper_config.yaml (current directory)
    2. ptc_tools_config.yaml (shared config file, current directory)
    3. config/ptc_sql_helper_config.yaml
    4. config/ptc_tools_config.yaml (shared config file)
    5. ~/.ptc_sql_helper_config.yaml
    6. ~/.ptc_tools_config.yaml (shared config file)
    """
    
    def __init__(self, config_file: Optional[str] = None, agent_id: Optional[str] = None):
        """
        Initialize SQL Helper tool
        
        Args:
            config_file: Path to YAML configuration file. If None, tries default locations.
            agent_id: Agent ID to load configuration from remote server. If provided, will try to load config from remote server first.
        """
        super().__init__(tool_name="sql_helper", config_file=config_file, agent_id=agent_id)
    
    def _extract_config(self, config_data: Dict[str, Any]):
        """Extract configuration from config data
        
        SQLHelper doesn't use llm and inner_llm, so override to skip them.
        
        Args:
            config_data: Configuration data dictionary
        """
        self.data_source = config_data.get('data_source', {})
        self.config = config_data.get('config', {})
    
    async def get_metadata(
        self,
        title: str,
        data_source: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """Get metadata information
        
        Args:
            title: Data title
            data_source: Data source configuration (optional). If None, uses config file value.
            config: Tool configuration (optional). If provided, merges with config file value (parameter takes precedence).
        
        Returns:
            Metadata information
        """
        logger.info(f"PTC sql_helper get_metadata title: {title}")
        
        data_source = data_source or self.data_source
        
        # Merge config: parameter config takes precedence over file config
        merged_config = self.config.copy()
        if config:
            merged_config.update(config)
        
        # Create DataView instance
        data_view = DataView(
            view_list=data_source.get('view_list', []),
            base_url=data_source.get('base_url', ''),
            token=data_source.get('token', ''),
            user_id=data_source.get('user_id', ''),
            account_type=data_source.get('account_type', 'user')
        )
        
        # Create SQLHelperTool instance
        tool = SQLHelperTool.from_data_source(
            data_source=data_view,
            **merged_config
        )
        
        # Call tool's ainvoke method
        result = await tool.ainvoke(input={
            "command": CommandType.GET_METADATA.value,
            "title": title
        })
        
        return result
    
    async def execute_sql(
        self,
        sql: str,
        data_source: Optional[Dict[str, Any]] = None,
        title: Optional[str] = "",
        config: Optional[Dict[str, Any]] = None
    ):
        """Execute SQL statement
        
        Args:
            sql: SQL statement to execute
            data_source: Data source configuration (optional). If None, uses config file value.
            title: Data title (optional), defaults to "SQL Execution Result"
            config: Tool configuration (optional). If provided, merges with config file value (parameter takes precedence).
        
        Returns:
            SQL execution result
        """
        logger.info(f"PTC sql_helper execute_sql sql: {sql}, title: {title}")
        
        data_source = data_source or self.data_source
        
        # Merge config: parameter config takes precedence over file config
        merged_config = self.config.copy()
        if config:
            merged_config.update(config)
        
        # Create DataView instance
        data_view = DataView(
            view_list=data_source.get('view_list', []),
            base_url=data_source.get('base_url', ''),
            token=data_source.get('token', ''),
            user_id=data_source.get('user_id', ''),
            account_type=data_source.get('account_type', 'user')
        )
        
        # Create SQLHelperTool instance
        tool = SQLHelperTool.from_data_source(
            data_source=data_view,
            **merged_config
        )
        
        # Call tool's ainvoke method
        result = await tool.ainvoke(input={
            "command": CommandType.EXECUTE_SQL.value,
            "sql": sql,
            "title": title or "SQL Execution Result"
        })
        
        return result
