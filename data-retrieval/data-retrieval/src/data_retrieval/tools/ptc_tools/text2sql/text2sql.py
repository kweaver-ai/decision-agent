# -*- coding: utf-8 -*-
# @Author:  Xavier.chen@aishu.cn
# @Date: 2025-01-XX
"""
PTC Text2SQL Tool

这是一个基于 PTC (Programmatic Tool Composition) 范式的 Text2SQL 工具实现。
直接调用 base_tools 中的 Text2SQLTool。
"""

from typing import Optional, Dict, Any

from data_retrieval.logs.logger import logger
from data_retrieval.tools.base_tools.text2sql import Text2SQLTool, ActionType
from data_retrieval.tools.ptc_tools.base import PTCBaseTool


class Text2SQL(PTCBaseTool):
    """PTC Text2SQL Tool
    
    Configuration is automatically loaded from YAML file.
    Default config file paths (in order):
    1. ptc_text2sql_config.yaml (current directory)
    2. config/ptc_text2sql_config.yaml
    3. ~/.ptc_text2sql_config.yaml
    """
    
    def __init__(self, config_file: Optional[str] = None, agent_id: Optional[str] = None):
        """
        Initialize Text2SQL tool
        
        Args:
            config_file: Path to YAML configuration file. If None, tries default locations.
            agent_id: Agent ID to load configuration from remote server. If provided, will try to load config from remote server first.
        """
        super().__init__(tool_name="text2sql", config_file=config_file, agent_id=agent_id)
    
    async def get_metadata(
        self,
        input: str = "",
        data_source: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """Get metadata information for data sources
        
        Args:
            input: Query description (optional, can be empty)
            data_source: Data source configuration (optional). If None, uses config file value.
            config: Tool configuration (optional). If provided, merges with config file value (parameter takes precedence).
        
        Returns:
            Data source metadata information
        """
        logger.info(f"PTC text2sql get_metadata input: {input}")
        
        data_source = data_source or self.data_source
        
        # Merge config: parameter config takes precedence over file config
        merged_config = self.config.copy()
        if config:
            merged_config.update(config)
        
        params = {
            "input": input or "",
            "action": ActionType.SHOW_DS.value,
            "data_source": data_source,
            "config": merged_config
        }
        
        # Add LLM configs from config file if available
        if self.llm:
            params["llm"] = self.llm
        if self.inner_llm:
            params["inner_llm"] = self.inner_llm
        
        result = await Text2SQLTool.as_async_api_cls(
            params=params,
            stream=False,
            mode="http"
        )
        
        return result
    
    async def generate_sql(
        self,
        input: str,
        data_source: Optional[Dict[str, Any]] = None,
        infos: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """Generate SQL from natural language without executing it
        
        Args:
            input: Natural language query from user
            data_source: Data source configuration (optional). If None, uses config file value.
            infos: Additional input information, including knowledge_enhanced_information and extra_info (optional)
            config: Tool configuration (optional). If provided, merges with config file value (parameter takes precedence).
        
        Returns:
            Result containing SQL and explanation, without execution results
        """
        logger.info(f"PTC text2sql generate_sql input: {input}")
        
        data_source = data_source or self.data_source
        if infos is None:
            infos = {}
        
        # Merge config: parameter config takes precedence over file config
        merged_config = self.config.copy()
        if config:
            merged_config.update(config)
        
        params = {
            "input": input,
            "action": ActionType.GEN.value,
            "data_source": data_source,
            "config": merged_config,
            "infos": infos
        }
        
        # Add LLM configs from config file if available
        if self.llm:
            params["llm"] = self.llm
        if self.inner_llm:
            params["inner_llm"] = self.inner_llm
        
        result = await Text2SQLTool.as_async_api_cls(
            params=params,
            stream=False,
            mode="http"
        )
        
        return result
    
    async def text2sql(
        self,
        input: str,
        data_source: Optional[Dict[str, Any]] = None,
        infos: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """Generate SQL from natural language and execute it
        
        Args:
            input: Natural language query from user
            data_source: Data source configuration (optional). If None, uses config file value.
            infos: Additional input information, including knowledge_enhanced_information and extra_info (optional)
            config: Tool configuration (optional). If provided, merges with config file value (parameter takes precedence).
        
        Returns:
            Result containing SQL, explanation, execution data, etc.
        """
        logger.info(f"PTC text2sql text2sql input: {input}")
        
        data_source = data_source or self.data_source
        if infos is None:
            infos = {}
        
        # Merge config: parameter config takes precedence over file config
        merged_config = self.config.copy()
        if config:
            merged_config.update(config)
        
        params = {
            "input": input,
            "action": ActionType.GEN_EXEC.value,
            "data_source": data_source,
            "config": merged_config,
            "infos": infos
        }
        
        # Add LLM configs from config file if available
        if self.llm:
            params["llm"] = self.llm
        if self.inner_llm:
            params["inner_llm"] = self.inner_llm
        
        result = await Text2SQLTool.as_async_api_cls(
            params=params,
            stream=False,
            mode="http"
        )
        
        return result
