# -*- coding: utf-8 -*-
# @Author:  Xavier.chen@aishu.cn
# @Date: 2025-01-XX
"""
PTC Tool Base Class

提供 PTC 工具的基础功能，包括配置加载等。
"""

from typing import Optional, Dict, Any
import os
import yaml
from abc import ABC

from data_retrieval.logs.logger import logger


class PTCBaseTool(ABC):
    """PTC Tool Base Class
    
    Provides common functionality for PTC tools, including configuration loading.
    Supports loading configuration from:
    1. Local YAML files
    2. Remote server via Agent ID
    """
    
    def __init__(
        self, 
        tool_name: str, 
        config_file: Optional[str] = None,
        agent_id: Optional[str] = None
    ):
        """
        Initialize PTC tool
        
        Args:
            tool_name: Tool name (used for config key and file name)
            config_file: Path to YAML configuration file. If None, tries default locations.
            agent_id: Agent ID to load configuration from remote server. If provided, will try to load config from remote server first.
        """
        self.tool_name = tool_name
        self.data_source: Dict[str, Any] = {}
        self.llm: Optional[Dict[str, Any]] = None
        self.inner_llm: Optional[Dict[str, Any]] = None
        self.config: Dict[str, Any] = {}
        
        self._load_config(config_file, agent_id)
    
    def _load_config(
        self, 
        config_file: Optional[str] = None,
        agent_id: Optional[str] = None
    ):
        """Load configuration from YAML file or remote server
        
        Supports two formats:
        1. Flat format (legacy): config at root level
        2. Nested format: config under '{tool_name}' key (for shared config files)
        
        Priority:
        1. If agent_id is provided, try to load from remote server first
        2. Then try config_file if provided
        3. Finally try default local file paths
        
        Args:
            config_file: Path to YAML configuration file. If None, tries default locations.
            agent_id: Agent ID to load configuration from remote server.
        """
        # Try to load from remote server if agent_id is provided
        if agent_id:
            config_data = self._load_config_from_remote(agent_id)
            if config_data:
                self._process_config_data(config_data)
                logger.info(f"Loaded configuration from remote server (agent_id: {agent_id})")
                return
            else:
                logger.warning(f"Failed to load config from remote server (agent_id: {agent_id}), falling back to local config")
        
        # Try to load from local files
        config_paths = []
        
        if config_file:
            config_paths.append(config_file)
        else:
            # Default config file paths
            dedicated_config_name = f"ptc_{self.tool_name}_config.yaml"
            config_paths = [
                dedicated_config_name,
                "ptc_tools_config.yaml",  # Shared config file
                f"config/{dedicated_config_name}",
                "config/ptc_tools_config.yaml",  # Shared config file
                os.path.expanduser(f"~/.{dedicated_config_name}"),
                os.path.expanduser("~/.ptc_tools_config.yaml")  # Shared config file
            ]
        
        for path in config_paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        config_data = yaml.safe_load(f) or {}
                    
                    self._process_config_data(config_data)
                    logger.info(f"Loaded configuration from {path}")
                    return
                except Exception as e:
                    logger.warning(f"Failed to load config from {path}: {e}")
        
        logger.info("No configuration file found, using empty defaults")
    
    def _load_config_from_remote(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Load configuration from remote server using Agent ID
        
        Args:
            agent_id: Agent ID to fetch configuration
            
        Returns:
            Configuration data dictionary, or None if failed
        """
        try:
            from data_retrieval.tools.graph_tools.driven.dip.agent_factory_service import agent_factory_service
            from data_retrieval.utils._common import run_blocking
            
            # Get agent config from remote server (async method, need to run blocking)
            agent_config = run_blocking(agent_factory_service.get_agent_config(agent_id))
            
            if not agent_config:
                logger.warning(f"Empty agent config returned for agent_id: {agent_id}")
                return None
            
            # Extract PTC tool configuration from agent config
            # Agent config structure: {"config": {...}, ...}
            # We need to extract the tool-specific config from agent config
            agent_config_data = agent_config.get("config", {})
            
            if not agent_config_data:
                logger.warning(f"No 'config' field found in agent config for agent_id: {agent_id}")
                return None
            
            # Try to find tool config in agent config
            # The tool config might be stored under a specific key or in the root
            if self.tool_name in agent_config_data and isinstance(agent_config_data[self.tool_name], dict):
                return agent_config_data[self.tool_name]
            elif "ptc_tools" in agent_config_data:
                ptc_tools_config = agent_config_data.get("ptc_tools", {})
                if isinstance(ptc_tools_config, dict) and self.tool_name in ptc_tools_config:
                    return ptc_tools_config[self.tool_name]
            
            # If not found under tool_name, try to use the whole config as flat format
            # This allows using the entire agent config as a flat configuration
            logger.info(f"Tool-specific config not found under '{self.tool_name}' or 'ptc_tools.{self.tool_name}', using entire agent config as flat format")
            return agent_config_data
            
        except ImportError:
            logger.warning("agent_factory_service not available, cannot load config from remote server")
            return None
        except Exception as e:
            logger.error(f"Error loading config from remote server (agent_id: {agent_id}): {e}")
            # Don't raise, let it fall back to local config
            return None
    
    def _process_config_data(self, config_data: Dict[str, Any]):
        """Process configuration data
        
        Args:
            config_data: Configuration data dictionary
        """
        # Try nested format first (for shared config files)
        if self.tool_name in config_data and isinstance(config_data[self.tool_name], dict):
            tool_config = config_data[self.tool_name]
            self._extract_config(tool_config)
        else:
            # Fall back to flat format (legacy)
            self._extract_config(config_data)
    
    def _extract_config(self, config_data: Dict[str, Any]):
        """Extract configuration from config data
        
        Subclasses can override this method to customize config extraction.
        
        Args:
            config_data: Configuration data dictionary
        """
        self.data_source = config_data.get('data_source', {})
        self.llm = config_data.get('llm')
        self.inner_llm = config_data.get('inner_llm')
        self.config = config_data.get('config', {})

