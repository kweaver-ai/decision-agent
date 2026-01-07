# -*- coding: utf-8 -*-
# @Author:  Xavier.chen@aishu.cn
# @Date: 2025-01-XX
"""
PTC Text2Metric Tool

这是一个基于 PTC (Programmatic Tool Composition) 范式的 Text2Metric 工具实现。
直接调用 base_tools 中的 Text2DIPMetricTool。
"""

from typing import Optional, Dict, Any

from data_retrieval.logs.logger import logger
from data_retrieval.tools.base_tools.text2dip_metric import Text2DIPMetricTool
from data_retrieval.tools.ptc_tools.base import PTCBaseTool


class Text2Metric(PTCBaseTool):
    """PTC Text2Metric Tool
    
    Configuration is automatically loaded from YAML file.
    Supports both dedicated config file (ptc_text2metric_config.yaml)
    and shared config file (ptc_tools_config.yaml with 'text2metric' key).
    
    Note: This tool uses Text2DIPMetricTool internally.
    """
    
    def __init__(self, config_file: Optional[str] = None, agent_id: Optional[str] = None):
        """
        Initialize Text2Metric tool
        
        Args:
            config_file: Path to YAML configuration file. If None, tries default locations.
            agent_id: Agent ID to load configuration from remote server. If provided, will try to load config from remote server first.
        """
        super().__init__(tool_name="text2metric", config_file=config_file, agent_id=agent_id)
    
    async def get_metadata(
        self,
        input: str = "",
        data_source: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """Get metadata information for DIP metrics
        
        Args:
            input: Query description (optional, can be empty)
            data_source: Data source configuration (optional). If None, uses config file value.
            config: Tool configuration (optional). If provided, merges with config file value (parameter takes precedence).
        
        Returns:
            DIP metric metadata information
        """
        logger.info(f"PTC text2metric get_metadata input: {input}")
        
        data_source = data_source or self.data_source
        
        # Merge config: parameter config takes precedence over file config
        merged_config = self.config.copy()
        if config:
            merged_config.update(config)
        
        params = {
            "input": input or "",
            "action": "show_ds",
            "data_source": data_source,
            "config": merged_config
        }
        
        # Add LLM configs from config file if available
        if self.llm:
            params["llm"] = self.llm
        if self.inner_llm:
            params["inner_llm"] = self.inner_llm
        
        result = await Text2DIPMetricTool.as_async_api_cls(
            params=params,
            stream=False,
            mode="http"
        )
        
        return result
    
    async def text2metric(
        self,
        input: str,
        data_source: Optional[Dict[str, Any]] = None,
        infos: Optional[Dict[str, Any]] = None,
        action: str = "query",
        config: Optional[Dict[str, Any]] = None
    ):
        """Generate DIP metric call parameters from natural language and execute
        
        Args:
            input: Natural language query from user
            data_source: Data source configuration (optional). If None, uses config file value.
            infos: Additional input information, including knowledge_enhanced_information and extra_info (optional)
            action: Action type, "show_ds" to show data source info, "query" to execute query (default)
            config: Tool configuration (optional). If provided, merges with config file value (parameter takes precedence).
        
        Returns:
            Result containing metric call parameters, execution data, etc.
        """
        logger.info(f"PTC text2metric text2metric input: {input}, action: {action}")
        
        data_source = data_source or self.data_source
        if infos is None:
            infos = {}
        
        # Merge config: parameter config takes precedence over file config
        merged_config = self.config.copy()
        if config:
            merged_config.update(config)
        
        params = {
            "input": input,
            "action": action,
            "data_source": data_source,
            "config": merged_config,
            "infos": infos
        }
        
        # Add LLM configs from config file if available
        if self.llm:
            params["llm"] = self.llm
        if self.inner_llm:
            params["inner_llm"] = self.inner_llm
        
        result = await Text2DIPMetricTool.as_async_api_cls(
            params=params,
            stream=False,
            mode="http"
        )
        
        return result

