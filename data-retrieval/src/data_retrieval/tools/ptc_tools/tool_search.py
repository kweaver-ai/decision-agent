# -*- coding: utf-8 -*-
# @Author:  Xavier.chen@aishu.cn
# @Date: 2025-01-XX
"""
PTC Tool Search Tool

搜索 PTC 工具并查看工具的说明文档。
"""

from typing import Optional, List, Dict, Any
from pathlib import Path
from langchain.pydantic_v1 import BaseModel, Field, PrivateAttr
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun
)

from data_retrieval.logs.logger import logger
from data_retrieval.tools.base import (
    LLMTool,
    ToolName,
    construct_final_answer,
    async_construct_final_answer,
)
from data_retrieval.tools.base import api_tool_decorator
from data_retrieval.utils.ranking import HybridRetriever
from data_retrieval.utils.embeddings import BaseEmbeddingsService, EmbeddingServiceFactory
from fastapi import Body

_INSTANCE = None


class ToolSearchInput(BaseModel):
    """Tool Search 工具的输入参数"""
    query: str = Field(
        default="",
        description="搜索查询语句，用于搜索相关的 PTC 工具"
    )
    tool_name: Optional[str] = Field(
        default=None,
        description="工具名称，如果提供则直接返回该工具的说明文档，忽略 query 参数"
    )
    topk: int = Field(
        default=5,
        description="返回结果数量，仅在搜索时有效"
    )
    tool_scope: Optional[List[str]] = Field(
        default=None,
        description="工具范围，指定要搜索的工具名称列表。如果为空，则搜索所有工具"
    )
    language: Optional[str] = Field(
        default=None,
        description="语言选项，用于过滤文档语言。可选值：'zh'（中文）、'en'（英文）。如果为 None，则搜索所有语言的文档"
    )


class ToolSearchTool(LLMTool):
    """PTC Tool Search Tool
    
    搜索 PTC 工具并查看工具的说明文档。
    使用混合检索（BM25 + 向量搜索）来搜索工具。
    
    当指定 tool_scope 时，从完整索引中过滤出需要的工具。
    """
    
    name: str = "tool_search"
    description: str = """搜索 PTC 工具并查看工具的说明文档。
    
    功能：
    1. 搜索工具：根据查询语句搜索相关的 PTC 工具
    2. 查看文档：获取指定工具的完整说明文档（usage.md）
    
    使用场景：
    - 需要查找特定功能的工具时使用搜索功能
    - 需要查看工具的详细使用方法时使用 tool_name 参数获取文档
    """
    args_schema: type[BaseModel] = ToolSearchInput
    
    # 实例级别的完整索引（单例共享）
    _full_name_retriever: Optional[HybridRetriever] = PrivateAttr(None)  # 工具名称索引
    _full_desc_retriever: Optional[HybridRetriever] = PrivateAttr(None)  # 工具+描述索引
    _full_tool_index: Dict[str, Dict[str, Any]] = PrivateAttr({})
    _full_name_corpus_kv: Dict[str, str] = PrivateAttr({})  # 名称索引语料库
    _full_desc_corpus_kv: Dict[str, str] = PrivateAttr({})  # 描述索引语料库
    _embedding_service: Optional[BaseEmbeddingsService] = PrivateAttr(None)
    _default_language: str = "zh"  # 默认语言：中文
    _supported_languages: List[str] = ["zh", "en"]  # 支持的语言列表
    _name_weight: float = 0.8  # 名称匹配权重
    _desc_weight: float = 0.2  # 描述匹配权重
    
    def _normalize_language(self, language: Optional[str]) -> str:
        """验证并规范化语言参数
        
        如果语言不支持，给出警告并使用默认语言。
        
        Args:
            language: 语言参数，可选值：'zh'（中文）、'en'（英文）
        
        Returns:
            规范化后的语言代码
        """
        if language is None:
            return self._default_language
        
        # 转换为小写以便比较
        language = language.lower().strip()
        
        # 验证语言是否支持
        if language not in self._supported_languages:
            logger.warning(f"Unsupported language: '{language}'. Supported languages: {self._supported_languages}. Using default language: {self._default_language}")
            return self._default_language
        
        return language
    
    def __init__(self, **kwargs):
        """
        初始化工具搜索
        
        单例模式：使用全局变量 _INSTANCE 实现单例。
        初始化时构建完整索引，搜索时如果指定 scope 则创建临时索引。
        
        Args:
            **kwargs: 其他参数
        """
        super().__init__(**kwargs)
        
        # 构建完整索引
        self._build_full_index()
    
    def _build_full_index(self):
        """构建完整索引（所有工具）
        
        支持带语言后缀的文档：usage.md, usage_zh.md, usage_en.md
        """
        try:
            # Create default embedding service
            factory = EmbeddingServiceFactory()
            self._embedding_service = factory.get_service()
            
            ptc_tools_dir = Path(__file__).parent
            
            # Find all usage files (支持 usage_zh.md, usage_en.md)
            usage_patterns = ["*/usage_zh.md", "*/usage_en.md"]
            usage_files = []
            for pattern in usage_patterns:
                usage_files.extend(ptc_tools_dir.glob(pattern))
            
            name_corpus_kv = {}  # 工具名称索引
            desc_corpus_kv = {}  # 工具+描述索引
            tool_index = {}
            
            for usage_file in usage_files:
                tool_name = usage_file.parent.name
                
                # Skip self
                if tool_name == "tool_search":
                    continue
                
                # Extract language from filename
                filename = usage_file.name
                if filename == "usage_zh.md":
                    language = "zh"
                elif filename == "usage_en.md":
                    language = "en"
                else:
                    continue  # 跳过不支持的格式
                
                try:
                    with open(usage_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extract summary for indexing
                    summary = self._extract_summary(content)
                    
                    # Create document ID with language suffix
                    doc_id = f"{tool_name}_{language}"
                    
                    # Store tool metadata (keep full content for document retrieval)
                    tool_index[doc_id] = {
                        "name": tool_name,
                        "content": content,
                        "summary": summary,
                        "language": language
                    }
                    
                    # 创建两个索引：
                    # 1. 名称索引：只包含工具名称
                    name_corpus_kv[doc_id] = tool_name
                    
                    # 2. 描述索引：工具名称 + 描述
                    desc_corpus_kv[doc_id] = f"{tool_name} {summary}"
                    
                    logger.info(f"Indexed tool: {tool_name} (language: {language})")
                except Exception as e:
                    logger.warning(f"Failed to index tool {tool_name} (language: {language}): {e}")
            
            self._full_tool_index = tool_index
            self._full_name_corpus_kv = name_corpus_kv
            self._full_desc_corpus_kv = desc_corpus_kv
            
            # 构建名称索引
            if name_corpus_kv and self._embedding_service:
                self._full_name_retriever = HybridRetriever(
                    emb_service=self._embedding_service,
                    corpus_kv=name_corpus_kv
                )
                logger.info("Building name search index...")
                self._full_name_retriever.build()
                logger.info(f"Name search index built with {len(name_corpus_kv)} tools")
            else:
                self._full_name_retriever = None
            
            # 构建描述索引
            if desc_corpus_kv and self._embedding_service:
                self._full_desc_retriever = HybridRetriever(
                    emb_service=self._embedding_service,
                    corpus_kv=desc_corpus_kv
                )
                logger.info("Building description search index...")
                self._full_desc_retriever.build()
                logger.info(f"Description search index built with {len(desc_corpus_kv)} tools")
            else:
                self._full_desc_retriever = None
            
            if not name_corpus_kv and not desc_corpus_kv:
                logger.warning("No tools found to index or embedding service unavailable")
        except Exception as e:
            logger.error(f"Failed to build full search index: {e}")
            self._full_retriever = None
            self._full_tool_index = {}
            self._full_corpus_kv = {}
    
    def _build_filtered_index(self, tool_scope: Optional[List[str]] = None, language: Optional[str] = None):
        """根据 tool_scope 和 language 构建过滤索引
        
        创建两个过滤后的索引：名称索引和描述索引
        
        Args:
            tool_scope: 工具范围，指定要搜索的工具名称列表。如果为 None，则搜索所有工具
            language: 语言选项，'zh'（中文）、'en'（英文）。如果为 None，则使用默认语言（中文）
        
        Returns:
            tuple: (name_retriever, desc_retriever, tool_index) 
                - name_retriever: 工具名称索引的 HybridRetriever 实例
                - desc_retriever: 工具+描述索引的 HybridRetriever 实例
                - tool_index: 工具索引字典，包含工具元数据
        """
        # 检查完整索引是否已构建
        if not self._full_tool_index:
            return None, None, {}
        
        # 验证并规范化语言参数
        language = self._normalize_language(language)
        
        # 从完整索引中过滤出符合条件的工具
        scope_set = set(tool_scope) if tool_scope else None
        filtered_tool_index = {}
        filtered_name_corpus_kv = {}
        filtered_desc_corpus_kv = {}
        
        for doc_id, tool_info in self._full_tool_index.items():
            tool_name = tool_info["name"]
            tool_language = tool_info.get("language")
            
            # 过滤 tool_scope
            if scope_set is not None and tool_name not in scope_set:
                continue
            
            # 过滤 language
            if tool_language != language:
                continue
            
            # 复制工具信息，避免修改原始索引
            filtered_tool_index[doc_id] = tool_info.copy()
            
            # 复制名称和描述索引的语料库
            if doc_id in self._full_name_corpus_kv:
                filtered_name_corpus_kv[doc_id] = self._full_name_corpus_kv[doc_id]
            if doc_id in self._full_desc_corpus_kv:
                filtered_desc_corpus_kv[doc_id] = self._full_desc_corpus_kv[doc_id]
        
        # 构建临时 retriever（仅当有过滤后的工具时）
        if not filtered_name_corpus_kv or not filtered_desc_corpus_kv:
            logger.warning(f"No tools found in scope: {tool_scope}, language: {language}")
            return None, None, filtered_tool_index
        
        if not self._embedding_service:
            logger.warning("Embedding service not available")
            return None, None, filtered_tool_index
        
        # 创建并构建名称索引 retriever
        name_retriever = HybridRetriever(
            emb_service=self._embedding_service,
            corpus_kv=filtered_name_corpus_kv
        )
        logger.info(f"Building filtered name search index for scope: {tool_scope}, language: {language} ({len(filtered_name_corpus_kv)} tools)")
        name_retriever.build()
        
        # 创建并构建描述索引 retriever
        desc_retriever = HybridRetriever(
            emb_service=self._embedding_service,
            corpus_kv=filtered_desc_corpus_kv
        )
        logger.info(f"Building filtered description search index for scope: {tool_scope}, language: {language} ({len(filtered_desc_corpus_kv)} tools)")
        desc_retriever.build()
        
        logger.info(f"Filtered search indexes built successfully")
        
        return name_retriever, desc_retriever, filtered_tool_index
    
    def _extract_summary(self, content: str) -> str:
        """从使用文档中提取摘要（支持中英文）
        
        支持以下 Overview 标题：
        - ## Overview (英文)
        - ## 概述 (中文)
        - ## 简介 (中文)
        """
        lines = content.split('\n')
        summary_lines = []
        in_overview = False
        
        # 支持中英文的 Overview 标题
        overview_markers = ['## Overview', '## 概述', '## 简介']
        
        for line in lines:
            line_stripped = line.strip()
            
            # 检查是否是 Overview 部分开始
            if any(line_stripped.startswith(marker) for marker in overview_markers):
                in_overview = True
                continue
            # 检查是否是下一个章节（以 ## 开头）
            elif in_overview and line_stripped.startswith('##'):
                break
            elif in_overview:
                summary_lines.append(line_stripped)
        
        summary = ' '.join(summary_lines).strip()
        return summary[:200] if summary else "No summary available"
    
    @construct_final_answer
    def _run(
        self,
        query: str = "",
        tool_name: Optional[str] = None,
        topk: int = 5,
        tool_scope: Optional[List[str]] = None,
        language: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ):
        """同步执行方法"""
        from data_retrieval.utils._common import run_blocking
        return run_blocking(self._arun(query, tool_name, topk, tool_scope, language, run_manager))
    
    @async_construct_final_answer
    async def _arun(
        self,
        query: str = "",
        tool_name: Optional[str] = None,
        topk: int = 5,
        tool_scope: Optional[List[str]] = None,
        language: Optional[str] = None,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ):
        """异步执行方法
        
        Args:
            query: 搜索查询语句
            tool_name: 工具名称，如果提供则直接返回该工具的说明文档
            topk: 返回结果数量
            tool_scope: 工具范围，指定要搜索的工具名称列表
            language: 语言选项，'zh'（中文）、'en'（英文）
            run_manager: 回调管理器
        """
        try:
            # 如果提供了 tool_name，直接返回该工具的说明文档
            if tool_name:
                return await self._handle_get_usage(tool_name, tool_scope, language)
            
            # 根据 tool_scope 和 language 获取索引（完整索引或过滤后的临时索引）
            name_retriever, desc_retriever, tool_index = self._build_filtered_index(tool_scope, language)
            
            # 如果没有查询，返回所有工具列表
            if not query:
                return self._handle_list_tools(tool_index, tool_scope)
            
            # 执行搜索（使用两个索引）
            return await self._handle_search(query, topk, name_retriever, desc_retriever, tool_index, tool_scope)
            
        except Exception as e:
            logger.error(f"Tool search failed: {e}")
            return {
                "action": "error",
                "error": str(e),
                "message": f"Tool search failed: {str(e)}"
            }
    
    async def _handle_get_usage(self, tool_name: str, tool_scope: Optional[List[str]], language: Optional[str] = None) -> dict:
        """处理获取工具文档请求"""
        # 验证并规范化语言参数
        language = self._normalize_language(language)
        logger.info(f"Getting usage document for tool: {tool_name}, language: {language}")
        
        # 检查工具是否在指定范围内
        if tool_scope and tool_name not in tool_scope:
            return {
                "action": "get_usage",
                "tool_name": tool_name,
                "usage_document": None,
                "message": f"Tool {tool_name} is not in the specified scope"
            }
        
        # 从完整索引中获取文档（根据 language 参数）
        usage_doc = self._get_tool_usage(tool_name, language)
        if usage_doc:
            return {
                "action": "get_usage",
                "tool_name": tool_name,
                "usage_document": usage_doc,
                "message": f"Successfully retrieved usage document for {tool_name}"
            }
        else:
            return {
                "action": "get_usage",
                "tool_name": tool_name,
                "usage_document": None,
                "message": f"Tool {tool_name} not found or usage document not available (language: {language})"
            }
    
    def _handle_list_tools(self, tool_index: Dict[str, Dict[str, Any]], tool_scope: Optional[List[str]]) -> dict:
        """处理列出工具请求"""
        # 提取唯一的工具名称（去重，因为可能有多个语言的文档）
        tools = list(set(tool_info["name"] for tool_info in tool_index.values()))
        tools.sort()  # 排序以便展示
        return {
            "action": "list_tools",
            "tools": tools,
            "count": len(tools),
            "tool_scope": tool_scope,
            "message": f"Found {len(tools)} available tools"
        }
    
    async def _handle_search(
        self,
        query: str,
        topk: int,
        name_retriever: Optional[HybridRetriever],
        desc_retriever: Optional[HybridRetriever],
        tool_index: Dict[str, Dict[str, Any]],
        tool_scope: Optional[List[str]]
    ) -> dict:
        """处理搜索请求
        
        同时搜索名称索引和描述索引，合并结果并加权（名称权重0.8，描述权重0.2）
        """
        logger.info(f"Searching for tools with query: '{query}', scope: {tool_scope}")
        
        # 检查 retriever 是否可用
        if not name_retriever or not desc_retriever:
            return {
                "action": "search",
                "query": query,
                "results": [],
                "message": "Search index not available"
            }
        
        # 同时搜索两个索引
        name_results = await name_retriever.asearch(query, topk=topk * 2)  # 获取更多结果用于合并
        desc_results = await desc_retriever.asearch(query, topk=topk * 2)
        
        # 合并结果并加权
        merged_scores = {}  # doc_id -> weighted_score
        
        # 处理名称匹配结果（权重0.8）
        for doc_id, score, rank_bm25, rank_vec in name_results:
            if doc_id not in tool_index:
                continue
            weighted_score = float(score) * self._name_weight
            merged_scores[doc_id] = weighted_score
        
        # 处理描述匹配结果（权重0.2）
        for doc_id, score, rank_bm25, rank_vec in desc_results:
            if doc_id not in tool_index:
                continue
            weighted_score = float(score) * self._desc_weight
            
            if doc_id in merged_scores:
                # 如果名称索引也匹配，合并分数
                merged_scores[doc_id] += weighted_score
            else:
                # 只在描述索引中匹配
                merged_scores[doc_id] = weighted_score
        
        # 按加权分数排序
        sorted_results = sorted(
            merged_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:topk]
        
        # 格式化搜索结果
        formatted_results = []
        for doc_id, weighted_score in sorted_results:
            tool_info = tool_index[doc_id].copy()
            tool_info["score"] = weighted_score
            # 移除完整内容以减少返回数据大小
            tool_info.pop("content", None)
            formatted_results.append(tool_info)
        
        return {
            "action": "search",
            "query": query,
            "results": formatted_results,
            "count": len(formatted_results),
            "tool_scope": tool_scope,
            "message": f"Found {len(formatted_results)} tools matching '{query}'"
        }
    
    def _get_tool_usage(self, tool_name: str, language: Optional[str] = None) -> Optional[str]:
        """获取工具的说明文档（从完整索引中获取）
        
        Args:
            tool_name: 工具名称
            language: 语言选项，'zh'（中文）、'en'（英文）。如果为 None，使用默认语言（中文）
        
        Returns:
            文档内容，如果未找到则返回 None
        """
        # 验证并规范化语言参数
        language = self._normalize_language(language)
        
        # 构建文档 ID
        doc_id = f"{tool_name}_{language}"
        
        # 从索引中获取
        if doc_id in self._full_tool_index:
            return self._full_tool_index[doc_id].get("content")
        
        # Fallback: try to read directly
        ptc_tools_dir = Path(__file__).parent
        usage_file = ptc_tools_dir / tool_name / f"usage_{language}.md"
        
        if usage_file.exists():
            try:
                with open(usage_file, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Failed to read usage file for {tool_name} (language: {language}): {e}")
                return None
        
        logger.warning(f"Usage file not found for tool: {tool_name} (language: {language})")
        return None
    
    @classmethod
    @api_tool_decorator
    async def as_async_api_cls(
        cls,
        params: dict = Body(...),
        stream: bool = False,
        mode: str = "http"
    ):
        """异步 API 调用方法"""
        logger.info(f"ToolSearchTool as_async_api_cls params: {params}")
        
        # 创建工具实例
        global _INSTANCE
        if _INSTANCE is None:
            _INSTANCE = cls()
        tool = _INSTANCE
        # tool = cls()
        
        query = params.get("query", "")
        tool_name = params.get("tool_name")
        topk = params.get("topk", 5)
        tool_scope = params.get("tool_scope")
        language = params.get("language")
        
        result = await tool.ainvoke({
            "query": query,
            "tool_name": tool_name,
            "topk": topk,
            "tool_scope": tool_scope,
            "language": language
        })
        
        return result
    
    @staticmethod
    async def get_api_schema():
        """获取 API Schema"""
        return {
            "post": {
                "summary": "tool_search",
                "description": "搜索 PTC 工具并查看工具的说明文档。支持根据查询语句搜索工具，或直接获取指定工具的说明文档。",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "query": {
                                        "type": "string",
                                        "description": "搜索查询语句，用于搜索相关的 PTC 工具"
                                    },
                                    "tool_name": {
                                        "type": "string",
                                        "description": "工具名称，如果提供则直接返回该工具的说明文档，忽略 query 参数"
                                    },
                                    "topk": {
                                        "type": "integer",
                                        "description": "返回结果数量，仅在搜索时有效",
                                        "default": 5
                                    },
                                    "tool_scope": {
                                        "type": "array",
                                        "items": {
                                            "type": "string"
                                        },
                                        "description": "工具范围，指定要搜索的工具名称列表。如果为空，则搜索所有工具"
                                    },
                                    "language": {
                                        "type": "string",
                                        "description": "语言选项，用于过滤文档语言。可选值：'zh'（中文）、'en'（英文）。如果为 None，则搜索所有语言的文档"
                                    }
                                }
                            },
                            "examples": {
                                "search": {
                                    "summary": "搜索工具",
                                    "value": {
                                        "query": "SQL execution",
                                        "topk": 3
                                    }
                                },
                                "get_usage": {
                                    "summary": "获取工具说明文档",
                                    "value": {
                                        "tool_name": "text2sql"
                                    }
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Successful operation",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "action": {
                                            "type": "string",
                                            "description": "操作类型：search, get_usage, list_tools"
                                        },
                                        "results": {
                                            "type": "array",
                                            "description": "搜索结果列表（搜索时返回）"
                                        },
                                        "usage_document": {
                                            "type": "string",
                                            "description": "工具的说明文档（获取文档时返回）"
                                        },
                                        "tools": {
                                            "type": "array",
                                            "description": "工具列表（列出工具时返回）"
                                        },
                                        "message": {
                                            "type": "string",
                                            "description": "操作结果消息"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
