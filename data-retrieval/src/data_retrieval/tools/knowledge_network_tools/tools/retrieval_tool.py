# -*- coding: utf-8 -*-
"""
基于知识网络的检索工具
实现五步检索流程：
1. 获取业务知识网络列表
2. 使用LLM判断用户查询相关的知识网络
3. 获取知识网络详情
4. 使用LLM判断相关的对象类型
5. 构建最终的检索结果
"""

import json
import os
import time
import yaml
from typing import List, Dict, Any, Optional, Tuple, Union, Set
from fastapi import Body, HTTPException, Header, Depends
from pydantic import BaseModel, Field
import asyncio
from datetime import datetime, timedelta
from collections import defaultdict

# 样例数据获取逻辑（从本文件抽离）
from ..infra.helpers.sample_data import fetch_sample_data_for_object_type, fetch_all_sample_data
# 纯工具函数（从本文件抽离）
from ..infra.helpers.tool_utils import (
    filter_properties_mapped_field,
    build_instance_dedup_key,
    merge_semantic_instances_maps,
)
from ..infra.helpers.semantic_output import (
    filter_semantic_instances_by_global_final_score_ratio,
    normalize_semantic_instances_for_output,
    semantic_instances_map_to_nodes,
)
from ..infra.helpers.schema_brief import to_brief_schema
from ..infra.helpers.schema_info import get_schema_info
from ..infra.helpers.final_result_builder import build_final_result
from ..services.pipeline.request_prep import normalize_kn_ids, normalize_retrieval_config
# 导入LLM客户端
from ..infra.clients.llm_client import LLMClient
# 导入日志模块
from data_retrieval.logs.logger import logger
# 导入重排序客户端
from data_retrieval.tools.graph_tools.driven.external.rerank_client import RerankClient
from ..infra.utils.timing_utils import set_timing_ctx, clear_timing_ctx, add_cost, compute_api_union_ms
# 导入标准错误响应类
from data_retrieval.errors import KnowledgeNetworkRetrievalError, KnowledgeNetworkParamError
# 导入Pydantic模型
from ..models import (
    KnowledgeNetworkRetrievalInput,
    KnowledgeNetworkInfo,
    ObjectTypeInfo,
    RelationTypeInfo,
    KnowledgeNetworkRetrievalResult,
    KnowledgeNetworkRetrievalResponse,
    HeaderParams,
    RetrievalConfig,
    SemanticInstanceRetrievalConfig,
    InstancePropertyFilterConfig
)
# 导入会话管理器
from ..services.session.session_manager import RetrievalSessionManager
# 导入HTTP客户端
from ..infra.clients.http_client import KnowledgeNetworkHTTPClient
# 导入知识网络检索模块
from ..core.retrieval.network_retrieval import KnowledgeNetworkRetrieval
# 导入概念检索模块
from ..core.retrieval.concept_retrieval import ConceptRetrieval
# 导入语义实例召回模块
from ..core.retrieval.semantic_instance_retrieval import SemanticInstanceRetrieval


class KnowledgeNetworkRetrievalTool:
    """基于知识网络的检索工具"""
    
    def __init__(self):
        pass
    
    @classmethod
    async def _fetch_sample_data_for_object_type(
        cls,
        kn_id: str,
        object_type_id: str,
        headers: Optional[Dict[str, str]] = None
    ) -> Optional[Dict[str, Any]]:
        """兼容接口：委托到 `retrieval/sample_data.py`。"""
        return await fetch_sample_data_for_object_type(kn_id, object_type_id, headers)
    
    @classmethod
    async def _fetch_all_sample_data(
        cls,
        kn_id: str,
        object_types: List[Dict[str, Any]],
        headers: Optional[Dict[str, str]] = None,
        max_concurrent: int = 10
    ) -> Dict[str, Optional[Dict[str, Any]]]:
        """兼容接口：委托到 `retrieval/sample_data.py`。"""
        return await fetch_all_sample_data(kn_id, object_types, headers, max_concurrent)
    
    @classmethod
    def _filter_properties_mapped_field(cls, properties: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """兼容接口：委托到 `retrieval/tool_utils.py`。"""
        return filter_properties_mapped_field(properties)
    
    @classmethod
    def _build_instance_dedup_key(
        cls,
        instance: Dict[str, Any],
        primary_keys: Optional[List[str]],
        display_key: Optional[str]
    ) -> str:
        """兼容接口：委托到 `retrieval/tool_utils.py`。"""
        return build_instance_dedup_key(instance, primary_keys, display_key)
    
    @classmethod
    def _merge_semantic_instances_maps(
        cls,
        keyword_results: List[Tuple[str, Dict[str, List[Dict[str, Any]]]]],
        schema_info: Optional[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """兼容接口：委托到 `retrieval/tool_utils.py`。"""
        return merge_semantic_instances_maps(keyword_results, schema_info)

    @classmethod
    def _normalize_semantic_instances_for_output(
        cls,
        semantic_instances_map: Optional[Dict[str, List[Dict[str, Any]]]],
        schema_info: Optional[Dict[str, Any]],
        property_filter_config: Optional[InstancePropertyFilterConfig] = None,
    ) -> Optional[Dict[str, List[Dict[str, Any]]]]:
        """兼容接口：委托到 `retrieval/semantic_output.py`。"""
        return normalize_semantic_instances_for_output(
            semantic_instances_map, schema_info, property_filter_config=property_filter_config
        )

    @classmethod
    def _semantic_instances_map_to_nodes(
        cls,
        semantic_instances_map: Optional[Dict[str, List[Dict[str, Any]]]]
    ) -> List[Dict[str, Any]]:
        """兼容接口：委托到 `retrieval/semantic_output.py`。"""
        return semantic_instances_map_to_nodes(semantic_instances_map)

    
    @classmethod
    def _to_brief_schema(cls, result: Dict[str, Any]) -> Dict[str, Any]:
        """兼容接口：委托到 `retrieval/schema_brief.py`。"""
        return to_brief_schema(result)
    
    @classmethod
    def _get_schema_info(
        cls,
        session_id: Optional[str],
        kn_id: str,
        network_details: Optional[Dict[str, Any]] = None,
        filtered_objects: Optional[Dict[str, Any]] = None,
        filtered_relations: Optional[List[Dict[str, Any]]] = None,
        raise_on_error: bool = False
    ) -> Optional[Dict[str, Any]]:
        """兼容接口：委托到 `retrieval/schema_info.py`。"""
        return get_schema_info(
            session_id=session_id,
            kn_id=kn_id,
            network_details=network_details,
            filtered_objects=filtered_objects,
            filtered_relations=filtered_relations,
            raise_on_error=raise_on_error,
        )
    
    @classmethod
    async def _build_final_result(
        cls,
        relevant_concepts: Tuple[Dict, List[Dict[str, Any]]],
        network_details: Dict[str, Any],
        session_id: Optional[str] = None,
        skip_llm: bool = False,
        return_union: bool = True,
        include_sample_data: bool = False,
        kn_id: Optional[str] = None,
        semantic_instances_map: Optional[Dict[str, List[Dict[str, Any]]]] = None,
        enable_property_brief: bool = False,
        per_object_property_top_k: int = 8,
        global_property_top_k: int = 30,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """兼容接口：委托到 `retrieval/final_result_builder.py`。"""
        return await build_final_result(
            relevant_concepts=relevant_concepts,
            network_details=network_details,
            session_id=session_id,
            skip_llm=skip_llm,
            return_union=return_union,
            include_sample_data=include_sample_data,
            kn_id=kn_id,
            semantic_instances_map=semantic_instances_map,
            enable_property_brief=enable_property_brief,
            per_object_property_top_k=per_object_property_top_k,
            global_property_top_k=global_property_top_k,
        )
    
    
    @classmethod
    async def retrieve(
        cls,
        query: str,
        kn_ids: List[Any] = None,
        additional_context: Optional[str] = None,
        session_id: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        retrieval_config: Optional[RetrievalConfig] = None,
        only_schema: bool = False,
        enable_rerank: bool = True
    ) -> tuple[Union[Dict[str, List[Dict[str, Any]]], Dict[str, Any]], float]:
        """
        执行知识网络检索
        
        Args:
            query: 用户查询问题（完整问题）
            kn_ids: 指定的知识网络配置列表，每个配置包含knowledge_network_id字段，必须传递
            additional_context: 额外的上下文信息，用于二次检索时提供更精确的检索信息
            session_id: 会话ID，用于保存检索结果到历史记录
            headers: HTTP请求头
            retrieval_config: 召回配置参数（RetrievalConfig对象），用于控制语义实例召回的实例数据阈值和数量
            only_schema: 是否只召回概念（schema），不召回语义实例。如果为True，则只返回object_types和relation_types，不返回nodes。默认为False。
            
        Returns:
            包含object_types和relation_types的字典和执行时间
        """
        req_start = time.monotonic()
        api_cost = {"detail": 0.0, "object_query": 0.0, "path_query": 0.0, "rerank": 0.0, "other": 0.0}
        set_timing_ctx(api_cost, req_start)
        kn_id_list = normalize_kn_ids(kn_ids)
            
        start_time = time.time()
        try:
            # 概念召回/流程参数统一从 retrieval_config.concept_retrieval 读取
            retrieval_config = normalize_retrieval_config(retrieval_config)

            concept_config = retrieval_config.get_concept_config() if retrieval_config else None
            top_k = concept_config.top_k if concept_config else 10
            skip_llm = concept_config.skip_llm if concept_config else True
            concept_return_union = concept_config.return_union if concept_config else False
            include_sample_data = concept_config.include_sample_data if concept_config else False
            schema_brief = concept_config.schema_brief if concept_config else False
            # 属性裁剪配置：LLM提示词与最终schema共用一套TopK参数
            per_object_property_top_k = (
                int(getattr(concept_config, "per_object_property_top_k", 8) or 8)
                if concept_config
                else 8
            )
            global_property_top_k = (
                int(getattr(concept_config, "global_property_top_k", 30) or 30)
                if concept_config
                else 30
            )
            # 默认开启裁剪（仅在 schema_brief 场景下生效）；可通过 concept_config.enable_property_brief 显式关闭
            enable_property_brief = (
                bool(getattr(concept_config, "enable_property_brief", True))
                if concept_config
                else bool(schema_brief)
            ) and bool(schema_brief)
            # only_schema 已废弃：schema 与语义实例解耦，语义实例统一通过 nodes 返回

            logger.info(f"开始执行知识网络检索（概念召回），查询: {query}")
            
            # 在每次请求开始时清理一次过期会话，但排除当前会话
            RetrievalSessionManager._clean_expired_sessions()
            
            # 从 headers 中提取 account_id 和 account_type（必需参数，已由HeaderParams验证）
            account_id = headers.get("x-account-id") if headers else None
            account_type = headers.get("x-account-type") if headers else None
            # 这两个参数现在是必需的，理论上不应该为None，但为了防御性编程，保留检查
            if not account_id:
                raise ValueError("x-account-id header参数不能为空")
            if not account_type:
                raise ValueError("x-account-type header参数不能为空")
            
            # 获取第一个知识网络ID（目前只支持单个知识网络）
            kn_id = kn_id_list[0] if kn_id_list else None
            if not kn_id:
                raise ValueError("kn_ids参数不能为空，必须提供至少一个知识网络配置")
            
            # 进行概念召回流程（schema召回）
            # 检查是否有概念召回缓存
            relevant_concepts = None
            network_details = None
            
            if session_id and RetrievalSessionManager.has_concept_retrieval_cache(session_id, kn_id, query):
                # 有缓存，直接使用缓存结果
                logger.info(f"发现概念召回缓存（session_id={session_id}, query={query[:50]}...），复用缓存结果")
                cached_result = RetrievalSessionManager.get_concept_retrieval_cache(session_id, kn_id, query)
                
                if cached_result:
                    relevant_concepts = cached_result["relevant_concepts"]  # (filtered_objects, filtered_relations)
                    network_details = cached_result["network_details"]
                    logger.info(f"成功复用概念召回缓存，对象类型: {len(relevant_concepts[0])} 项，关系类型: {len(relevant_concepts[1])} 项")
                else:
                    # 缓存获取失败，继续执行概念召回
                    logger.warning("概念召回缓存获取失败，继续执行概念召回")
                    relevant_concepts = None
                    network_details = None
            
            # 如果没有缓存结果，执行概念召回
            if relevant_concepts is None or network_details is None:
                # 检查session中是否有schema信息，判断是首次召回还是多轮召回
                if session_id and RetrievalSessionManager.has_schema_info(session_id, kn_id):
                    # 已有schema信息，这是多轮的概念召回
                    logger.info(f"Session中已有schema信息，进行多轮概念召回")
                else:
                    # 没有schema信息，这是首次概念召回
                    logger.info(f"Session中没有schema信息，进行首次概念召回")
                
                # 使用KnowledgeNetworkRetrieval获取相关知识网络和详情，目前只会获取一个知识网络
                network_details = await KnowledgeNetworkRetrieval._rank_knowledge_networks(
                    query,
                    top_k,
                    additional_context,
                    headers,
                    session_id,
                    kn_id_list,
                    account_id=account_id,
                    account_type=account_type,
                    concept_config=concept_config,
                    enable_rerank=enable_rerank,
                )
                logger.info(f"获取知识网络详情")
                
                # 如果需要获取样例数据，在概念召回之前先获取并存储到session
                if include_sample_data and session_id:
                    # 检查session中是否已有样例数据
                    if not RetrievalSessionManager.has_sample_data(session_id, kn_id):
                        logger.info(f"Session中没有样例数据，开始获取所有对象类型的样例数据")
                        # 获取所有对象类型
                        object_types = network_details.get("object_types", [])
                        if object_types:
                            # 并发获取所有对象类型的样例数据
                            sample_data_dict = await cls._fetch_all_sample_data(
                                kn_id=kn_id,
                                object_types=object_types,
                                headers=headers,
                                max_concurrent=10
                            )
                            # 存储到session
                            RetrievalSessionManager.set_all_sample_data(session_id, kn_id, sample_data_dict)
                            logger.info(f"样例数据获取完成并已存储到session，共 {len(sample_data_dict)} 个对象类型")
                        else:
                            logger.warning(f"知识网络 {kn_id} 没有对象类型，跳过样例数据获取")
                    else:
                        logger.info(f"Session中已有样例数据，跳过样例数据获取")
                
                # 步骤4: 使用LLM判断相关的关系类型
                logger.info(f"跳过关系类型的LLM检索，直接使用前{top_k}个关系类型")
                # 调用ConceptRetrieval.rank_relation_types方法，但跳过LLM处理，直接返回前top_k个关系
                relevant_concepts = await ConceptRetrieval.rank_relation_types(
                    query,
                    network_details,
                    top_k,
                    additional_context,
                    session_id,
                    skip_llm=skip_llm,
                    account_id=account_id,
                    account_type=account_type,
                    per_object_property_top_k=per_object_property_top_k,
                    global_property_top_k=global_property_top_k,
                    enable_rerank=enable_rerank,
                )
                
                logger.info(f"筛选出相关概念")
                
                # 存储到缓存
                if session_id:
                    RetrievalSessionManager.set_concept_retrieval_cache(
                        session_id, kn_id, query, relevant_concepts, network_details
                    )
                    logger.info(f"概念召回结果已缓存")
            
            # 步骤5: 语义实例召回（与 schema 统一返回）
            # 对召回的对象类型进行语义实例召回；若没有对象类型则自然为空。
            semantic_instances_map: Dict[str, List[Dict[str, Any]]] = {}

            # 如果 only_schema=True，跳过语义实例召回
            if only_schema:
                logger.info("only_schema=True，跳过语义实例召回，只返回概念（schema，包括object_types、relation_types和action_types）")
            else:
                # 处理语义实例召回配置
                if isinstance(retrieval_config, dict):
                    retrieval_config = RetrievalConfig.from_dict(retrieval_config)
                semantic_config = (
                    retrieval_config.get_semantic_config()
                    if isinstance(retrieval_config, RetrievalConfig) else SemanticInstanceRetrievalConfig()
                )
                # enable_rerank 参数不再存储在 semantic_config 中，而是通过函数参数直接传递
                # 外层的 enable_rerank 参数会在调用各个函数时直接传递

                filtered_objects, filtered_relations = relevant_concepts
                if filtered_objects:
                    property_filter_config = (
                        retrieval_config.get_property_filter_config()
                        if isinstance(retrieval_config, RetrievalConfig) else InstancePropertyFilterConfig()
                    )

                    # 解析多关键词（空格分隔），控制上限防止膨胀
                    keywords_for_search = [query]
                    if isinstance(query, str):
                        splitted = [p.strip() for p in query.split() if p.strip()]
                        if len(splitted) > 1:
                            max_keywords = 5
                            keywords_for_search = splitted[:max_keywords]
                            if len(splitted) > max_keywords:
                                logger.warning(f"多关键词输入数量 {len(splitted)} 超过上限 {max_keywords}，仅使用前 {max_keywords} 个")
                            logger.info(f"多关键词语义召回，关键词列表: {keywords_for_search}")

                    # 当只有单个关键词时，允许使用缓存；多关键词场景下不复用缓存，避免误混
                    can_use_cache = len(keywords_for_search) == 1

                    # 提前构建 schema_info：缓存复用与后续语义召回都需要它（display_key/primary_keys）
                    schema_info = cls._get_schema_info(
                        session_id=session_id,
                        kn_id=kn_id,
                        network_details=network_details,
                        filtered_objects=filtered_objects,
                        filtered_relations=filtered_relations,
                        raise_on_error=False
                    )
                    if not schema_info:
                        logger.warning("无法获取schema_info，语义实例召回输出将无法基于display_key进行精简")

                    if can_use_cache and session_id and RetrievalSessionManager.has_semantic_instance_cache(session_id, kn_id, query):
                        # 有缓存，直接使用缓存结果
                        logger.info(f"发现语义实例召回缓存（session_id={session_id}, query={query[:50]}...），复用缓存结果")
                        cached_result = RetrievalSessionManager.get_semantic_instance_cache(session_id, kn_id, query)

                        if cached_result:
                            semantic_instances_map = cached_result["semantic_instances_map"]
                            # 全局分数过滤（抑制低质尾部噪声）
                            try:
                                if getattr(semantic_config, "enable_global_final_score_ratio_filter", True):
                                    ratio = float(getattr(semantic_config, "global_final_score_ratio", 0.25) or 0.25)
                                    semantic_instances_map = filter_semantic_instances_by_global_final_score_ratio(
                                        semantic_instances_map, ratio=ratio, keep_at_least_one=True
                                    )
                            except Exception:
                                # 过滤失败不影响主流程
                                pass
                            # 统一规范化输出（兼容历史缓存中字段未剔除的情况）
                            semantic_instances_map = cls._normalize_semantic_instances_for_output(
                                semantic_instances_map, schema_info, property_filter_config=property_filter_config
                            )
                            logger.info(f"成功复用语义实例召回缓存，共 {len(semantic_instances_map)} 个对象类型有实例数据")
                        else:
                            # 缓存获取失败，继续执行语义实例召回
                            logger.warning("语义实例召回缓存获取失败，继续执行语义实例召回")
                            semantic_instances_map = None
                    else:
                        semantic_instances_map = None
                        logger.debug("没有缓存或缓存不可用，semantic_instances_map设为None，将执行语义实例召回")
                    
                    # 如果没有缓存结果，执行语义实例召回
                    if semantic_instances_map is None:
                        logger.debug("进入语义实例召回分支：semantic_instances_map为None，开始执行语义实例召回")
                        # 构建对象类型列表（用于语义实例召回）
                        object_types_for_retrieval = []
                        for obj in filtered_objects.values():
                            object_types_for_retrieval.append({
                                "concept_id": obj.get("id"),
                                "concept_name": obj.get("name"),
                                "data_properties": obj.get("data_properties", [])
                            })
                        
                        # schema_info 已在上方提前构建；此处仅兜底
                        if not schema_info:
                            logger.warning("无法获取schema_info，语义实例召回可能无法正常工作")
                        
                        # candidate_limit和per_type_instance_limit现在都有默认值，不需要回退逻辑
                        semantic_per_type_limit = semantic_config.per_type_instance_limit
                        semantic_candidate_limit = semantic_config.initial_candidate_count
                        # 预过滤阶段每个对象类型保留的上限，若未配置则退化为 per_type_instance_limit
                        pre_filter_per_type_limit = getattr(semantic_config, "pre_filter_per_type_limit", None) \
                            or semantic_per_type_limit
                        
                        keyword_results: List[Tuple[str, Dict[str, List[Dict[str, Any]]]]] = []
                        if filtered_objects:
                            # 方案B（优化版）：多关键词合并为"每对象类型一次候选召回"，再用完整query统一过滤/重排
                            if len(keywords_for_search) > 1:
                                logger.info(
                                    f"开始多关键词候选召回（合并请求），关键词数={len(keywords_for_search)}，对象类型数={len(object_types_for_retrieval)}, "
                                    f"candidate_limit={semantic_candidate_limit}"
                                )
                                candidate_instance_map = await SemanticInstanceRetrieval.semantic_retrieve_candidates_for_all_multi_keyword(
                                    full_query=query,
                                    keywords=keywords_for_search,
                                    object_types=object_types_for_retrieval,
                                    kn_id=kn_id,
                                    schema_info=schema_info or {},
                                    headers=headers,
                                    candidate_limit=semantic_candidate_limit,
                                    max_concurrent=5,
                                    timeout=5.0,
                                    semantic_config=semantic_config,
                                    # 多关键词合并默认不带 ==，避免 sub_conditions 爆炸
                                    include_exact_match=False,
                                    enable_rerank=enable_rerank,  # 传递 enable_rerank 参数
                                )

                                # 统一补充 keyword_sources 便于调试（该候选来自"合并请求"，不代表逐关键词命中）
                                try:
                                    for obj_id, inst_list in (candidate_instance_map or {}).items():
                                        if not isinstance(inst_list, list):
                                            continue
                                        for inst in inst_list:
                                            if isinstance(inst, dict) and "keyword_sources" not in inst:
                                                inst["keyword_sources"] = list(keywords_for_search)
                                except Exception:
                                    pass
                                
                                # 使用完整query进行最终过滤/重排（体现关键词组合意图）
                                logger.info(
                                    f"多关键词候选召回完成，候选实例数={sum(len(v) for v in (candidate_instance_map or {}).values())}"
                                )
                                prefiltered_instance_map = await SemanticInstanceRetrieval.rerank_instance_map(
                                    instance_map=candidate_instance_map,
                                    query=query,
                                    schema_info=schema_info or {},
                                    per_type_top_k=pre_filter_per_type_limit,
                                    enable_rerank=enable_rerank
                                )
                                semantic_instances_map = await SemanticInstanceRetrieval.filter_instance_map_with_filtering(
                                    instance_map=prefiltered_instance_map,
                                    query=query,
                                    object_types=object_types_for_retrieval,
                                    kn_id=kn_id,
                                    schema_info=schema_info or {},
                                    headers=headers,
                                    semantic_config=semantic_config
                                )
                                
                                logger.info(f"语义实例召回完成（方案B：候选并集+统一过滤），对象类型数={len(semantic_instances_map)}")
                            else:
                                async def _run_kw(kw: str) -> Tuple[str, Dict[str, List[Dict[str, Any]]]]:
                                    logger.info(
                                        f"开始语义实例召回（并发关键词），关键词='{kw}'，对象类型数={len(object_types_for_retrieval)}, "
                                        f"per_type_instance_limit={semantic_per_type_limit}, candidate_limit={semantic_candidate_limit}"
                                    )
                                    kw_map = await SemanticInstanceRetrieval.semantic_retrieve_instances_for_all(
                                        query=kw,
                                        object_types=object_types_for_retrieval,
                                        kn_id=kn_id,
                                        schema_info=schema_info,
                                        headers=headers,
                                        per_type_instance_limit=semantic_per_type_limit,
                                        candidate_limit=semantic_candidate_limit,
                                        max_concurrent=5,  # 最大并发数
                                        timeout=5.0,
                                        semantic_config=semantic_config,  # 传递配置，启用过滤功能
                                        enable_rerank=enable_rerank,  # 传递 enable_rerank 参数
                                    )
                                    return kw, (kw_map or {})
                            
                                # 关键词之间并发执行；如任一关键词失败，将直接抛出异常（不吞异常）
                                keyword_results = await asyncio.gather(*[_run_kw(kw) for kw in keywords_for_search])
                                # 合并去重
                                semantic_instances_map = cls._merge_semantic_instances_maps(keyword_results, schema_info)
                                logger.info(f"语义实例召回完成（合并多关键词），对象类型数={len(semantic_instances_map)}")
                        
                        # 存储到缓存（仅单关键词场景）
                        if can_use_cache and session_id and semantic_instances_map is not None:
                            # 全局分数过滤（抑制低质尾部噪声）
                            try:
                                if getattr(semantic_config, "enable_global_final_score_ratio_filter", True):
                                    ratio = float(getattr(semantic_config, "global_final_score_ratio", 0.25) or 0.25)
                                    semantic_instances_map = filter_semantic_instances_by_global_final_score_ratio(
                                        semantic_instances_map, ratio=ratio, keep_at_least_one=True
                                    )
                            except Exception:
                                pass
                            semantic_instances_map = cls._normalize_semantic_instances_for_output(
                                semantic_instances_map, schema_info, property_filter_config=property_filter_config
                            )
                            RetrievalSessionManager.set_semantic_instance_cache(
                                session_id, kn_id, query, semantic_instances_map
                            )
                            logger.info(f"语义实例召回结果已缓存")
                        elif semantic_instances_map is not None:
                            # 全局分数过滤（抑制低质尾部噪声）
                            try:
                                if getattr(semantic_config, "enable_global_final_score_ratio_filter", True):
                                    ratio = float(getattr(semantic_config, "global_final_score_ratio", 0.25) or 0.25)
                                    semantic_instances_map = filter_semantic_instances_by_global_final_score_ratio(
                                        semantic_instances_map, ratio=ratio, keep_at_least_one=True
                                    )
                            except Exception:
                                pass
                            # 非缓存场景也规范化输出
                            semantic_instances_map = cls._normalize_semantic_instances_for_output(
                                semantic_instances_map, schema_info, property_filter_config=property_filter_config
                            )
                else:
                    # 没有filtered_objects，不进行语义实例召回
                    logger.info("没有召回的对象类型，跳过语义实例召回")
                    semantic_instances_map = {}

            # 步骤6: 构建 schema 结果（object_types/relation_types/action_types）
            final_result = await cls._build_final_result(
                relevant_concepts,
                network_details,
                session_id,
                skip_llm,
                concept_return_union,
                include_sample_data=include_sample_data,
                kn_id=kn_id,
                # NOTE: 语义实例不再绑定在 object_types 下
                semantic_instances_map=None,
                enable_property_brief=enable_property_brief,
                per_object_property_top_k=per_object_property_top_k,
                global_property_top_k=global_property_top_k,
            )

            # 生成当前轮 nodes（扁平结构）
            # 如果 only_schema=True，不返回 nodes 和 message
            if not only_schema:
                current_nodes = cls._semantic_instances_map_to_nodes(semantic_instances_map or {})

                # 多轮：将 nodes 写入 session，并按 concept_return_union 返回并集/增量
                if session_id and kn_id:
                    try:
                        current_round = RetrievalSessionManager.add_semantic_nodes_result(
                            session_id=session_id,
                            kn_id=kn_id,
                            nodes=current_nodes,
                            query=query,
                        )
                        nodes_to_return = RetrievalSessionManager.compute_semantic_nodes_return(
                            session_id=session_id,
                            kn_id=kn_id,
                            current_nodes=current_nodes,
                            return_union=bool(concept_return_union),
                            current_round=current_round or None,
                        )
                    except Exception:
                        nodes_to_return = current_nodes
                else:
                    nodes_to_return = current_nodes

                final_result["nodes"] = nodes_to_return
                if not nodes_to_return:
                    final_result["message"] = "未查询到相关实例数据"

            logger.info(
                "构建完成，schema对象类型=%d，关系类型=%d，nodes=%d",
                len(final_result.get("object_types", []) or []),
                len(final_result.get("relation_types", []) or []),
                len(final_result.get("nodes", []) or []),
            )
            
            # 根据schema_brief开关返回精简结果（仅裁剪 schema 字段，不影响 nodes/message）
            if schema_brief and "object_types" in final_result:
                logger.info("schema_brief=True，返回精简schema（保留 nodes/message）")
                final_result = cls._to_brief_schema(final_result)
            
            execution_time = time.time() - start_time
            total_ms = (time.monotonic() - req_start) * 1000
            api_union_ms = compute_api_union_ms()
            compute_ms = max(total_ms - api_union_ms, 0.0)
            # 简洁耗时日志：总耗时、API真实耗时（并集）、API分项、代码计算耗时
            logger.info(
                "耗时 | 总: %.1fms | API真实: %.1fms | 代码计算: %.1fms | session=%s kn=%s query=%s",
                total_ms,
                api_union_ms,
                compute_ms,
                session_id,
                kn_id,
                str(query)[:60],
            )
            try:
                # 分桶“真实耗时”（并集/墙钟口径）：用于判断哪类接口最影响整体延迟
                bucket_union_ms = {k: compute_api_union_ms(k) for k in api_cost.keys()}
                max_bucket, max_ms = max(bucket_union_ms.items(), key=lambda x: x[1])
                logger.info(
                    "API真实分桶(并集)：详情=%.1fms, 对象=%.1fms, 路径=%.1fms, 重排=%.1fms, 其他=%.1fms | 最长类型=%s(%.1fms)",
                    bucket_union_ms["detail"],
                    bucket_union_ms["object_query"],
                    bucket_union_ms["path_query"],
                    bucket_union_ms["rerank"],
                    bucket_union_ms["other"],
                    max_bucket,
                    max_ms,
                )
            except Exception:
                # 计时埋点不影响主流程
                pass
            logger.info(f"知识网络检索完成，执行时间: {execution_time:.2f}秒")
            return final_result, execution_time
            
        except Exception as e:
            logger.error(f"知识网络检索过程中出现错误: {str(e)}", exc_info=True)
            raise
        finally:
            clear_timing_ctx()

    @classmethod
    async def as_async_api_cls(cls, params: dict = Body(...), header_params: HeaderParams = Depends()):
        """
        API接口方法
        
        Args:
            params: API请求参数
            header_params: 请求头参数对象
            
        Returns:
            检索结果列表
        """
        try:
            # 参数验证阶段
            try:
                print(params)
                print(header_params)
                # 验证参数  
                input_data = KnowledgeNetworkRetrievalInput(**params)

                # 概念流程参数统一从 retrieval_config.concept_retrieval 读取
                cfg_obj = input_data.retrieval_config or RetrievalConfig()
                concept_cfg = cfg_obj.get_concept_config() if cfg_obj else None
                
                # 构建headers字典
                headers_dict = {
                    "x-account-type": header_params.account_type,
                    "x-account-id": header_params.account_id,
                    "Content-Type": header_params.content_type
                }
                logger.debug("请求头构建完成")
            except Exception as e:
                logger.error(f"参数验证失败: {str(e)}")
                raise KnowledgeNetworkParamError(
                    detail={"error": str(e)},
                    link="https://example.com/api-docs/knowledge-network-retrieval"
                )
            
            # 执行检索阶段
            try:
                # 执行检索
                result, execution_time = await cls.retrieve(
                    query=input_data.query,
                    kn_ids=input_data.kn_ids,
                    additional_context=input_data.additional_context,
                    session_id=input_data.session_id,
                    headers=headers_dict,
                    retrieval_config=input_data.retrieval_config,
                    only_schema=input_data.only_schema,
                    enable_rerank=input_data.enable_rerank
                )
                logger.debug("知识网络检索执行完成")
                
                # schema_brief 走精简返回，避免再做Pydantic包装
                if concept_cfg and concept_cfg.schema_brief:
                    return result
                
                # 统一返回 schema（object_types/relation_types/action_types），并兼容返回 nodes/message
                nodes = result.get("nodes")
                message = result.get("message")

                # 返回完整格式
                api_result = {
                    "object_types": [],
                    "relation_types": []
                }
                
                # 处理对象类型（包含属性信息）
                for obj_item in result.get("object_types", []):
                    # 对象类型不包含kn_id、source_object_type_id、target_object_type_id字段
                    api_item = {k: v for k, v in obj_item.items() 
                           if k not in ["kn_id", "source_object_type_id", "target_object_type_id"]}
                    
                    # 确保data_properties字段始终是列表（即使为空）
                    properties = api_item.get("data_properties")
                    if properties is None:
                        api_item["data_properties"] = []
                    elif not isinstance(properties, list):
                        api_item["data_properties"] = []
                    else:
                        # 过滤掉属性中的mapped_field字段
                        api_item["data_properties"] = cls._filter_properties_mapped_field(properties)
                    
                    # 处理sample_data字段：如果include_sample_data=False，不包含该字段
                    # 如果include_sample_data=True，包含该字段（即使为None）
                    if (concept_cfg and not concept_cfg.include_sample_data) and "sample_data" in api_item:
                        # 如果不需要样例数据，移除该字段
                        del api_item["sample_data"]
                
                    # 确保logic_properties字段为列表（非精简模式下返回）
                    logic_properties = api_item.get("logic_properties")
                    if logic_properties is None:
                        api_item["logic_properties"] = []
                    elif not isinstance(logic_properties, list):
                        api_item["logic_properties"] = []
                    
                    # 确保primary_keys存在（即使为空列表），便于下游消费多主键信息
                    if "primary_keys" not in api_item:
                        api_item["primary_keys"] = []
                    
                    # 创建Pydantic对象
                    # 注意：api_item已经排除了source_object_type_id和target_object_type_id
                    # 但Pydantic模型定义了这些字段（默认None），所以序列化时会包含
                    # 我们稍后在最终响应中统一清理
                    api_result["object_types"].append(KnowledgeNetworkRetrievalResult(**api_item))
                
                # 处理关系类型（不包含属性信息）
                for rel_item in result.get("relation_types", []):
                    api_item = {k: v for k, v in rel_item.items() if k not in ["kn_id", "data_properties"]}
                    api_result["relation_types"].append(KnowledgeNetworkRetrievalResult(**api_item))
                    
                logger.debug(f"结果转换完成，对象类型: {len(api_result['object_types'])} 项，关系类型: {len(api_result['relation_types'])} 项")
                
                # 获取action_types（如果存在）
                action_types = result.get("action_types")
                
                # 构建响应对象
                response_obj = KnowledgeNetworkRetrievalResponse(
                    object_types=api_result["object_types"],
                    relation_types=api_result["relation_types"],
                    action_types=action_types,
                    nodes=nodes,
                    message=message,
                )
                
                # 转换为字典
                response_dict = response_obj.model_dump()
                
                # 清理对象类型中的source_object_type_id和target_object_type_id字段
                # 注意：即使这些字段值为None，Pydantic也会在序列化时包含它们
                # 所以我们需要手动删除对象类型中的这两个字段
                for obj_type in response_dict.get("object_types", []):
                    # 明确删除这两个字段（对象类型不应该有这些字段）
                    if "source_object_type_id" in obj_type:
                        del obj_type["source_object_type_id"]
                    if "target_object_type_id" in obj_type:
                        del obj_type["target_object_type_id"]
                
                # 清理关系类型中不需要的字段（data_properties/primary_key_field/sample_data）
                for rel_type in response_dict.get("relation_types", []):
                    rel_type.pop("data_properties", None)
                    rel_type.pop("logic_properties", None)
                    rel_type.pop("primary_keys", None)
                    rel_type.pop("sample_data", None)
                    # 关系类型不包含实例字段
                
                # 返回清理后的字典（FastAPI会自动序列化）
                return response_dict
            except KnowledgeNetworkRetrievalError:
                # 已经是标准化的知识网络错误，直接向上抛出，保留原始 detail 信息
                raise
            except Exception as e:
                # 其它未预期异常，统一包装为 KnowledgeNetworkRetrievalError，
                # 将具体错误信息透传到 detail.error 中，方便调用方定位问题
                logger.error(f"知识网络检索执行失败: {str(e)}", exc_info=True)
                raise KnowledgeNetworkRetrievalError(
                    detail={"error": str(e)},
                    link="https://example.com/api-docs/knowledge-network-retrieval"
                )
        except HTTPException:
            # 重新抛出 HTTPException，保持原有行为
            raise
        except (KnowledgeNetworkRetrievalError, KnowledgeNetworkParamError) as e:
            # 将自定义异常转换为标准化错误响应
            raise HTTPException(
                status_code=400 if isinstance(e, KnowledgeNetworkParamError) else 500,
                detail=e.json()
            )
    
    @classmethod
    async def get_api_schema(cls):
        """获取API schema定义"""
        return {
            "post": {
                "summary": "kn_search",
                "description": "基于知识网络的智能检索工具，支持传入完整的问题或一个或多个关键词，能够检索问题或关键词的属性信息和上下文信息。",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "query": {
                                        "type": "string",
                                        "description": "用户查询问题或关键词，多个关键词之间用空格隔开"
                                    },
                                    "enable_rerank": {
                                        "type": "boolean",
                                        "description": "是否启用向量重排序。False时使用降级策略（粗召回分数、关键词匹配等）。适用于没有重排序模型的环境。",
                                        "default": True
                                    },
                                    "kn_ids": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "knowledge_network_id": {
                                                    "type": "string",
                                                    "description": "知识网络ID"
                                                }
                                            },
                                            "required": ["knowledge_network_id"]
                                        },
                                        "description": "指定的知识网络配置列表，必须传递，每个配置包含knowledge_network_id字段"
                                    },
                                    "session_id": {
                                        "type": "string",
                                        "description": "会话ID，用于维护多轮对话存储的历史召回记录",
                                        "nullable": True
                                    },
                                    "additional_context": {
                                        "type": "string",
                                        "description": "额外的上下文信息，用于二次检索时提供更精确的检索信息",
                                        "nullable": True
                                    },
                                    "retrieval_config": {
                                        "type": "object",
                                        "description": "召回配置参数，用于控制不同类型的召回场景（概念召回、语义实例召回、属性过滤）。如果不提供，将使用系统默认配置。",
                                        "nullable": True,
                                        "properties": {
                                            "concept_retrieval": {
                                                "type": "object",
                                                "description": "概念召回/概念流程配置参数（原最外层参数已收敛到此处）",
                                                "nullable": True,
                                                "properties": {
                                                    "top_k": {
                                                        "type": "integer",
                                                        "description": "概念召回返回最相关关系类型数量（对象类型会随关系类型自动过滤）。",
                                                        "minimum": 1,
                                                        "default": 10
                                                    },
                                                    "skip_llm": {
                                                        "type": "boolean",
                                                        "description": "是否跳过LLM筛选相关关系类型，直接使用前top_k个关系类型（高召回/低成本）。",
                                                        "default": True
                                                    },
                                                    "return_union": {
                                                        "type": "boolean",
                                                        "description": "概念召回多轮检索时是否返回并集。True返回所有轮次并集；False仅返回当前轮次增量（默认False）。",
                                                        "default": False
                                                    },
                                                    "include_sample_data": {
                                                        "type": "boolean",
                                                        "description": "是否获取对象类型的样例数据。True会为每个召回对象类型获取一条样例数据。",
                                                        "default": False
                                                    },
                                                    "schema_brief": {
                                                        "type": "boolean",
                                                        "description": "概念召回时是否返回精简schema。True仅返回必要字段（概念ID/名称/关系source&target），不返回大字段。",
                                                        "default": True
                                                    },
                                                    "enable_coarse_recall": {
                                                        "type": "boolean",
                                                        "description": "是否在概念召回前启用对象/关系粗召回，用于在大规模知识网络中先裁剪候选集合。",
                                                        "default": True
                                                    },
                                                    "coarse_object_limit": {
                                                        "type": "integer",
                                                        "description": "对象类型粗召回的最大返回数量，用于限制候选对象规模。",
                                                        "minimum": 1,
                                                        "default": 2000
                                                    },
                                                    "coarse_relation_limit": {
                                                        "type": "integer",
                                                        "description": "关系类型粗召回的最大返回数量，用于限制候选关系规模。",
                                                        "minimum": 1,
                                                        "default": 300
                                                    },
                                                    "coarse_min_relation_count": {
                                                        "type": "integer",
                                                        "description": "仅当知识网络内关系类型总数达到该阈值时才启用粗召回；小规模网络直接走精排流程。",
                                                        "minimum": 1,
                                                        "default": 5000
                                                    },
                                                    "enable_property_brief": {
                                                        "type": "boolean",
                                                        "description": "在 schema_brief=True 时，是否对返回的对象属性做相关性裁剪（每对象TopK，全局TopK）。",
                                                        "default": True
                                                    },
                                                    "per_object_property_top_k": {
                                                        "type": "integer",
                                                        "description": "属性裁剪时，每个对象类型最多保留的属性数量。生产环境建议值：8-10，适配表多、字段多的场景。",
                                                        "minimum": 1,
                                                        "default": 8
                                                    },
                                                    "global_property_top_k": {
                                                        "type": "integer",
                                                        "description": "属性裁剪时，全局最多保留的属性总数量。生产环境建议值：30-50，确保在多对象类型场景下保留足够的全局属性信息。",
                                                        "minimum": 1,
                                                        "default": 30
                                                    }
                                                }
                                            },
                                            "semantic_instance_retrieval": {
                                                "type": "object",
                                                "description": "语义实例召回配置参数",
                                                "nullable": True,
                                                "properties": {
                                                    "initial_candidate_count": {
                                                        "type": "integer",
                                                        "description": "语义实例召回的初始召回数量上限（重排序前的候选数量）。建议值：一般设置为per_type_instance_limit的3-5倍。",
                                                        "minimum": 1,
                                                        "default": 50
                                                    },
                                                    "per_type_instance_limit": {
                                                        "type": "integer",
                                                        "description": "每个对象类型最终返回的实例数量上限（重排序后的数量）。每个对象类型单独控制。",
                                                        "minimum": 1,
                                                        "default": 5
                                                    },
                                                    "max_semantic_sub_conditions": {
                                                        "type": "integer",
                                                        "description": "语义实例召回构造查询条件时 sub_conditions 的最大数量上限（用于适配后端限制与控成本）。默认10。",
                                                        "minimum": 1,
                                                        "default": 10
                                                    },
                                                    "semantic_field_keep_ratio": {
                                                        "type": "number",
                                                        "description": "语义字段筛选保留比例（按重排序分数Top-K保留）。例如0.2表示保留前20%的字段。",
                                                        "minimum": 0.01,
                                                        "maximum": 1.0,
                                                        "default": 0.2
                                                    },
                                                    "semantic_field_keep_min": {
                                                        "type": "integer",
                                                        "description": "语义字段筛选最少保留字段数（字段较少时兜底）。",
                                                        "minimum": 1,
                                                        "default": 5
                                                    },
                                                    "semantic_field_keep_max": {
                                                        "type": "integer",
                                                        "description": "语义字段筛选最多保留字段数（字段很多时强力限流）。",
                                                        "minimum": 1,
                                                        "default": 15
                                                    },
                                                    "semantic_field_rerank_batch_size": {
                                                        "type": "integer",
                                                        "description": "字段语义打分（rerank）时的批处理大小，字段数很大时会分批调用重排序服务。",
                                                        "minimum": 1,
                                                        "default": 128
                                                    },
                                                    "min_direct_relevance": {
                                                        "type": "number",
                                                        "description": "直接相关性最低阈值（0-1之间）。过滤掉直接相关性分数低于此阈值的实例。",
                                                        "minimum": 0.0,
                                                        "maximum": 1.0,
                                                        "default": 0.3
                                                    },
                                                    "enable_global_final_score_ratio_filter": {
                                                        "type": "boolean",
                                                        "description": "是否启用全局 final_score 相对阈值过滤。启用后仅保留 final_score >= max_final_score * global_final_score_ratio 的实例。",
                                                        "default": True
                                                    },
                                                    "global_final_score_ratio": {
                                                        "type": "number",
                                                        "description": "全局 final_score 相对阈值比例 r（0~1）。当 enable_global_final_score_ratio_filter=True 时，仅保留 final_score >= max_final_score * r 的实例。",
                                                        "minimum": 0.0,
                                                        "maximum": 1.0,
                                                        "default": 0.25
                                                    },
                                                    "exact_name_match_score": {
                                                        "type": "number",
                                                        "description": "多关键词检索场景下的实例名完全相等保底分（0~1）。当 query 被拆分为多个关键词时，只要任一关键词与 instance_name 完全相等，则会将该实例的基础语义分提升到该值，避免被其他关键词（如症状词）稀释后丢失。",
                                                        "minimum": 0.0,
                                                        "maximum": 1.0,
                                                        "default": 0.85
                                                    }
                                                }
                                            },
                                            "property_filter": {
                                                "type": "object",
                                                "description": "实例属性过滤配置（通用，适用于所有实例召回）",
                                                "nullable": True,
                                                "properties": {
                                                    "max_properties_per_instance": {
                                                        "type": "integer",
                                                        "description": "每个实例最多返回的属性字段数量。用于过滤实例属性，减少返回结果大小。",
                                                        "minimum": 1,
                                                        "default": 20
                                                    },
                                                    "max_property_value_length": {
                                                        "type": "integer",
                                                        "description": "属性值的最大长度（字符数），超过此长度的字段值会被过滤。",
                                                        "minimum": 1,
                                                        "default": 500
                                                    },
                                                    "enable_property_filter": {
                                                        "type": "boolean",
                                                        "description": "是否启用实例属性过滤。如果为False，返回所有属性字段。",
                                                        "default": True
                                                    }
                                                }
                                            }
                                        }
                                    },
                                    "only_schema": {
                                        "type": "boolean",
                                        "description": "是否只召回概念（schema），不召回语义实例。如果为True，则只返回object_types、relation_types和action_types，不返回nodes。默认为False。",
                                        "default": False
                                    }
                                },
                                "required": ["query", "kn_ids"]
                            },
                            "examples": {
                                "basic_query": {
                                    "summary": "基本查询示例",
                                    "description": "一个基本的知识网络检索查询示例",
                                    "value": {
                                        "query": "查询化工企业使用的催化剂信息",
                                        "kn_ids": [
                                            {
                                                "knowledge_network_id": "129"
                                            }
                                        ],
                                        "retrieval_config": {
                                            "concept_retrieval": {
                                                "top_k": 10
                                            }
                                        }
                                    }
                                },
                                "query_with_context": {
                                    "summary": "带上下文的查询示例",
                                    "description": "一个带有额外上下文信息的查询示例，用于二次检索",
                                    "value": {
                                        "query": "查询化工企业使用的催化剂信息",
                                        "kn_ids": [
                                            {
                                                "knowledge_network_id": "129"
                                            }
                                        ],
                                        "additional_context": "用户之前查询了关于化工企业的信息，现在想了解相关的催化剂",
                                        "retrieval_config": {
                                            "concept_retrieval": {
                                                "top_k": 10
                                            }
                                        }
                                    }
                                },
                                "query_with_kn_ids": {
                                    "summary": "指定知识网络ID的查询示例",
                                    "description": "一个指定了特定知识网络ID的查询示例",
                                    "value": {
                                        "query": "查询化工企业使用的催化剂信息",
                                        "kn_ids": [
                                            {
                                                "knowledge_network_id": "129"
                                            }
                                        ],
                                        "retrieval_config": {
                                            "concept_retrieval": {
                                                "top_k": 10
                                            }
                                        }
                                    }
                                },
                                "query_with_session": {
                                    "summary": "多轮对话查询示例",
                                    "description": "一个带有会话ID的查询示例，用于多轮对话场景",
                                    "value": {
                                        "query": "查询化工企业使用的催化剂信息",
                                        "kn_ids": [
                                            {
                                                "knowledge_network_id": "129"
                                            }
                                        ],
                                        "session_id": "user_session_123",
                                        "additional_context": "用户之前查询了关于化工企业的信息，现在想了解相关的催化剂",
                                        "retrieval_config": {
                                            "concept_retrieval": {
                                                "top_k": 10,
                                                "return_union": False
                                            }
                                        }
                                    }
                                },
                                "query_with_semantic_instance": {
                                    "summary": "语义实例召回查询示例",
                                    "description": "一个使用语义实例召回的查询示例",
                                    "value": {
                                        "query": "查询化工企业使用的催化剂信息",
                                        "kn_ids": [
                                            {
                                                "knowledge_network_id": "129"
                                            }
                                        ],
                                        "session_id": "user_session_123",
                                        "retrieval_config": {
                                            "concept_retrieval": {
                                                "top_k": 10
                                            },
                                            "semantic_instance_retrieval": {
                                                "initial_candidate_count": 50,
                                                "per_type_instance_limit": 10
                                            }
                                        }
                                    }
                                },
                                "query_with_property_brief": {
                                    "summary": "属性裁剪配置查询示例",
                                    "description": "一个展示属性裁剪配置的查询示例，适用于生产环境表多、字段多的场景",
                                    "value": {
                                        "query": "查询化工企业使用的催化剂信息",
                                        "kn_ids": [
                                            {
                                                "knowledge_network_id": "129"
                                            }
                                        ],
                                        "retrieval_config": {
                                            "concept_retrieval": {
                                                "top_k": 10,
                                                "schema_brief": True,
                                                "enable_property_brief": True,
                                                "per_object_property_top_k": 8,
                                                "global_property_top_k": 30,
                                                "enable_coarse_recall": True,
                                                "coarse_object_limit": 2000,
                                                "coarse_relation_limit": 300
                                            },
                                            "semantic_instance_retrieval": {
                                                "initial_candidate_count": 50,
                                                "per_type_instance_limit": 10
                                            },
                                            "property_filter": {
                                                "max_properties_per_instance": 20,
                                                "enable_property_filter": True
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "parameters": [
                    {
                        "name": "x-account-id",
                        "in": "header",
                        "required": True,
                        "schema": {
                            "type": "string"
                        },
                        "description": "账户ID，用于内部服务调用时传递账户信息（必需）"
                    },
                    {
                        "name": "x-account-type",
                        "in": "header",
                        "required": True,
                        "schema": {
                            "type": "string",
                            "enum": ["user", "app", "anonymous"]
                        },
                        "description": "账户类型：user(用户), app(应用), anonymous(匿名)（必需）"
                    },
                    {
                        "name": "Content-Type",
                        "in": "header",
                        "required": False,
                        "schema": {
                            "type": "string",
                            "default": "application/json"
                        },
                        "description": "内容类型"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Successful operation",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "description": "检索结果，返回object_types/relation_types/action_types，并返回语义实例nodes/message。多轮时由concept_retrieval.return_union控制 nodes 的并集/增量。",
                                    "properties": {
                                        "object_types": {
                                            "type": "array",
                                            "description": "对象类型列表（概念召回时返回）。当schema_brief=True时，仅包含：concept_id, concept_name, comment, data_properties（仅name和display_name）, logic_properties（仅name和display_name）, sample_data（当include_sample_data=True时）。当schema_brief=False时，包含完整字段（包括primary_keys, display_key, sample_data等）",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "concept_type": {
                                                        "type": "string",
                                                        "description": "概念类型: object_type",
                                                        "nullable": True
                                                    },
                                                    "concept_id": {
                                                        "type": "string",
                                                        "description": "概念ID"
                                                    },
                                                    "concept_name": {
                                                        "type": "string",
                                                        "description": "概念名称"
                                                    },
                                                    "comment": {
                                                        "type": "string",
                                                        "description": "概念描述",
                                                        "nullable": True
                                                    },
                                                    "data_properties": {
                                                        "type": "array",
                                                        "description": "对象属性列表。精简模式下仅包含name和display_name字段（数量不截断）",
                                                        "items": {
                                                            "type": "object",
                                                            "description": "对象属性",
                                                            "properties": {
                                                                "name": {
                                                                    "type": "string",
                                                                    "description": "属性名称",
                                                                    "nullable": True
                                                                },
                                                                "display_name": {
                                                                    "type": "string",
                                                                    "description": "属性显示名称",
                                                                    "nullable": True
                                                                },
                                                                "comment": {
                                                                    "type": "string",
                                                                    "description": "属性描述（非精简模式）",
                                                                    "nullable": True
                                                                }
                                                            }
                                                        },
                                                        "nullable": True
                                                    },
                                                    "logic_properties": {
                                                        "type": "array",
                                                        "description": "逻辑属性列表（指标等）。精简模式下仅包含name和display_name字段（数量不截断）",
                                                        "items": {
                                                            "type": "object",
                                                            "description": "逻辑属性",
                                                            "properties": {
                                                                "name": {
                                                                    "type": "string",
                                                                    "description": "属性名称",
                                                                    "nullable": True
                                                                },
                                                                "display_name": {
                                                                    "type": "string",
                                                                    "description": "属性显示名称",
                                                                    "nullable": True
                                                                }
                                                            }
                                                        },
                                                        "nullable": True
                                                    },
                                                    "primary_keys": {
                                                        "type": "array",
                                                        "description": "主键字段列表（支持多个主键）。仅当schema_brief=False时返回",
                                                        "items": {
                                                            "type": "string"
                                                        },
                                                        "nullable": True
                                                    },
                                                    "display_key": {
                                                        "type": "string",
                                                        "description": "显示字段名（用于获取instance_name）。仅当schema_brief=False时返回",
                                                        "nullable": True
                                                    },
                                                    "sample_data": {
                                                        "type": "object",
                                                        "description": "样例数据（当include_sample_data=True时返回，无论schema_brief是否为True）",
                                                        "nullable": True
                                                    },
                                                   
                                                },
                                                "required": [
                                                    "concept_id",
                                                    "concept_name"
                                                ]
                                            }
                                        },
                                        "relation_types": {
                                            "type": "array",
                                            "description": "关系类型列表（概念召回时返回）。精简模式和完整模式均包含：concept_id, concept_name, source_object_type_id, target_object_type_id",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "concept_type": {
                                                        "type": "string",
                                                        "description": "概念类型: relation_type",
                                                        "nullable": True
                                                    },
                                                    "concept_id": {
                                                        "type": "string",
                                                        "description": "概念ID"
                                                    },
                                                    "concept_name": {
                                                        "type": "string",
                                                        "description": "概念名称"
                                                    },
                                                    "source_object_type_id": {
                                                        "type": "string",
                                                        "description": "源对象类型ID"
                                                    },
                                                    "target_object_type_id": {
                                                        "type": "string",
                                                        "description": "目标对象类型ID"
                                                    }
                                                },
                                                "required": [
                                                    "concept_id",
                                                    "concept_name",
                                                    "source_object_type_id",
                                                    "target_object_type_id"
                                                ]
                                            }
                                        },
                                        "action_types": {
                                            "type": "array",
                                            "description": "操作类型列表（概念召回时返回）。当schema_brief=True时，每个action_type仅包含以下字段：id, name, action_type, object_type_id, object_type_name, comment, tags, kn_id",
                                            "nullable": True,
                                            "items": {
                                                "type": "object",
                                                "description": "操作类型信息。精简模式（schema_brief=True）下仅包含：id, name, action_type, object_type_id, object_type_name, comment, tags, kn_id",
                                                "properties": {
                                                    "id": {
                                                        "type": "string",
                                                        "description": "操作类型ID"
                                                    },
                                                    "name": {
                                                        "type": "string",
                                                        "description": "操作类型名称"
                                                    },
                                                    "action_type": {
                                                        "type": "string",
                                                        "description": "操作类型（如：add, modify等）"
                                                    },
                                                    "object_type_id": {
                                                        "type": "string",
                                                        "description": "对象类型ID"
                                                    },
                                                    "object_type_name": {
                                                        "type": "string",
                                                        "description": "对象类型名称"
                                                    },
                                                    "comment": {
                                                        "type": "string",
                                                        "description": "注释说明",
                                                        "nullable": True
                                                    },
                                                    "tags": {
                                                        "type": "array",
                                                        "description": "标签列表",
                                                        "items": {
                                                            "type": "string"
                                                        },
                                                        "nullable": True
                                                    },
                                                    "kn_id": {
                                                        "type": "string",
                                                        "description": "知识网络ID"
                                                    }
                                                }
                                            }
                                        },
                                        "nodes": {
                                            "type": "array",
                                            "description": "语义实例召回结果（当不提供conditions且召回到实例时返回），与条件召回节点风格对齐的扁平列表",
                                            "nullable": True,
                                            "items": {
                                                "type": "object",
                                                "description": "节点数据，至少包含 object_type_id、<object_type_id>_name、unique_identities",
                                                "properties": {
                                                    "object_type_id": {"type": "string"},
                                                    "unique_identities": {"type": "object"}
                                                }
                                            }
                                        },
                                        "message": {
                                            "type": "string",
                                            "description": "提示信息（例如未召回到实例数据时返回原因说明）",
                                            "nullable": True
                                        }
                                    }
                                }
                            }
                            }
                        }
                    }
                }
            }