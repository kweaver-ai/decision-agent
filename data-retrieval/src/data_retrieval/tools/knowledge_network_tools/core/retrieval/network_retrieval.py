# -*- coding: utf-8 -*-
"""
知识网络检索模块
实现知识网络检索相关的逻辑：
1. 获取业务知识网络列表
2. 使用LLM判断用户查询相关的知识网络
3. 获取知识网络详情
"""

import json
import time
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field

# 导入LLM客户端
from ...infra.clients.llm_client import LLMClient
# 导入日志模块
from data_retrieval.logs.logger import logger
# 导入重排序客户端
from data_retrieval.tools.graph_tools.driven.external.rerank_client import RerankClient
# 导入会话管理器
from ...services.session.session_manager import RetrievalSessionManager
# 导入HTTP客户端
from ...infra.clients.http_client import KnowledgeNetworkHTTPClient
# 导入标准错误响应类
from data_retrieval.errors import KnowledgeNetworkRetrievalError
# 导入统一排序工具
from ...infra.utils.ranking_utils import UnifiedRankingUtils, RankingStrategy


class KnowledgeNetworkRetrieval:
    """知识网络检索类"""
    
    def __init__(self):
        pass

    

    @classmethod
    async def _filter_all_relation_paths_with_rerank(
        cls,
        query: str,
        kn_ids: List[str],
        network_details: Dict[str, Dict[str, Any]],
        session_id: Optional[str] = None,
        top_k_per_network: int = 3,
        top_k_total: int = 10,
        enable_rerank: bool = True,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        一次性对所有知识网络的关系路径进行向量重排序，为每个知识网络选择前top_k_per_network个关系路径，最终选择top_k_total个最相关的关系路径
        
        Args:
            query: 用户查询
            kn_ids: 知识网络ID列表
            network_details: 知识网络详情字典
            session_id: 会话ID，用于缓存管理
            top_k_per_network: 每个知识网络选择的关系路径数量，默认为3
            top_k_total: 最终选择的关系路径总数量，默认为10
            
        Returns:
            按知识网络ID分组的过滤后的关系类型字典
        """
        # 收集所有知识网络的关系路径
        all_relation_types = []
        all_obj_id_to_name = {}
        kn_id_to_obj_mapping = {}  # 记录每个知识网络的对象类型映射
        
        for kn_id in kn_ids:
            if kn_id in network_details and "relation_types" in network_details[kn_id]:
                # 收集关系类型（此处 network_details 已可被上游粗召回裁剪）
                relation_types = network_details[kn_id].get("relation_types") or []
                for rel_type in relation_types:
                    # 添加知识网络ID到关系类型中
                    rel_type_with_kn = rel_type.copy()
                    rel_type_with_kn["knowledge_network_id"] = kn_id
                    all_relation_types.append(rel_type_with_kn)

                # 收集对象类型映射
                obj_id_to_name = {
                    obj_type.get("id", ""): obj_type.get("name", obj_type.get("id", ""))
                    for obj_type in (network_details[kn_id].get("object_types") or [])
                }
                kn_id_to_obj_mapping[kn_id] = obj_id_to_name
                all_obj_id_to_name.update(obj_id_to_name)
        
        if not all_relation_types:
            logger.debug("所有知识网络的关系类型列表为空，直接返回空字典")
            return {}
            
        # 构造关系路径文本用于重排序
        relation_texts = []
        relation_mapping = []  # 记录文本索引到关系类型的映射
        for rel_type in all_relation_types:
            # 获取源对象和目标对象名称
            source_name = all_obj_id_to_name.get(rel_type.get("source_object_type_id"), "未知")
            target_name = all_obj_id_to_name.get(rel_type.get("target_object_type_id"), "未知")
            rel_name = rel_type.get("name", rel_type.get("id", "未知"))
            
            # 构造自然语言描述
            relation_text = f"xx{source_name}{rel_name}xx{target_name}"
            relation_texts.append(relation_text)
            relation_mapping.append(rel_type)
        
        # 如果没有关系文本，直接返回空字典
        if not relation_texts:
            logger.debug("关系文本列表为空，直接返回空字典")
            return {}
        
        # 如果禁用重排序，使用降级策略
        if not enable_rerank:
            logger.info(f"[向量重排序] 关系路径重排序：enable_rerank=False，跳过向量重排序，使用降级策略（粗召回分数/关键词匹配），关系路径数量={len(relation_texts)}")
            return cls._filter_relation_paths_with_fallback(
                query, kn_ids, network_details, all_relation_types, relation_mapping,
                all_obj_id_to_name, top_k_per_network, top_k_total, session_id
            )
            
        try:
            # 使用RerankClient进行向量重排序
            logger.info(f"[向量重排序] 关系路径重排序：enable_rerank=True，使用向量重排序服务，关系路径数量={len(relation_texts)}")
            rerank_client = RerankClient()
            t0 = time.monotonic()
            try:
                logger.debug(f"[向量重排序] 调用RerankClient.ado_rerank进行关系路径重排序，query长度={len(query)}")
                rerank_scores = await rerank_client.ado_rerank(relation_texts, query)
                logger.debug(f"[向量重排序] RerankClient.ado_rerank返回，分数数量={len(rerank_scores) if rerank_scores else 0}")
            finally:
                elapsed_ms = (time.monotonic() - t0) * 1000
                try:
                    from ...infra.utils.timing_utils import add_cost
                    add_cost("rerank", elapsed_ms)
                except Exception:
                    pass
            
            # 确保返回有效的分数列表
            if rerank_scores and len(rerank_scores) > 0:
                # 新格式: [{"relevance_score": 0.985, "index": 1, "document": null}, ...]
                # 需要根据index重新排序并提取分数
                sorted_scores = sorted(rerank_scores, key=lambda x: x["index"])
                validated_scores = [float(item["relevance_score"]) for item in sorted_scores 
                                  if isinstance(item["relevance_score"], (int, float))]
                
                # 创建文本到分数的映射，用于日志记录
                relation_scores = {}
                for i, score in enumerate(validated_scores):
                    if i < len(relation_texts):
                        relation_scores[relation_texts[i]] = score
                # 取前5个分数最高的打印
                top_scores = sorted(relation_scores.items(), key=lambda x: x[1], reverse=True)[:5]
                if top_scores:
                    score_lines = []
                    for idx, (rel_text, score) in enumerate(top_scores, 1):
                        score_lines.append(f"  {idx}. {rel_text}: {score:.6f}")
                    logger.debug(f"关系路径分数映射（前5个）:\n" + "\n".join(score_lines))
                else:
                    logger.debug("关系路径分数映射: 无数据")
                
                # 将关系路径和分数配对
                scored_relations = []
                for i, score in enumerate(validated_scores):
                    if i < len(relation_mapping):
                        rel_type = relation_mapping[i]
                        rel_text = relation_texts[i]
                        scored_relations.append((score, rel_type, rel_text))
                        
                        # 将分数结果保存到会话管理器中
                        if session_id:
                            kn_id = rel_type.get("knowledge_network_id")
                            relation_id = rel_type.get('id', '')
                            if kn_id and relation_id:
                                RetrievalSessionManager.add_relation_score(session_id, kn_id, relation_id, score)
                
                # 按知识网络分组
                grouped_relations = {}
                for score, rel_type, rel_text in scored_relations:
                    network_id = rel_type.get("knowledge_network_id")
                    if network_id not in grouped_relations:
                        grouped_relations[network_id] = []
                    grouped_relations[network_id].append((score, rel_type, rel_text))
                
                # 为每个知识网络选择前top_k_per_network个关系路径
                selected_relations_by_kn = {}
                for network_id, relations in grouped_relations.items():
                    # 按分数降序排序
                    relations.sort(key=lambda x: x[0], reverse=True)
                    # 选择前top_k_per_network个
                    selected_relations_by_kn[network_id] = [rel[1] for rel in relations[:top_k_per_network]]
                
                # 如果所有知识网络的关系路径总数超过top_k_total，则按分数全局排序并选择前top_k_total个
                all_selected_relations = []
                for network_id, relations in grouped_relations.items():
                    all_selected_relations.extend(relations[:top_k_per_network])
                
                if len(all_selected_relations) > top_k_total:
                    # 按分数降序排序所有选中的关系路径
                    all_selected_relations.sort(key=lambda x: x[0], reverse=True)
                    
                    # 重新构建结果，确保总数不超过top_k_total
                    final_selected_relations_by_kn = {}
                    count = 0
                    for score, rel_type, rel_text in all_selected_relations:
                        network_id = rel_type.get("knowledge_network_id")
                        if network_id not in final_selected_relations_by_kn:
                            final_selected_relations_by_kn[network_id] = []
                        final_selected_relations_by_kn[network_id].append(rel_type)
                        count += 1
                        if count >= top_k_total:
                            break
                    
                    logger.debug(f"关系路径重排序完成，原始数量: {len(all_relation_types)}, 过滤后数量: {count}")
                    return final_selected_relations_by_kn
                else:
                    logger.debug(f"关系路径重排序完成，原始数量: {len(all_relation_types)}, 过滤后数量: {len(all_selected_relations)}")
                    return selected_relations_by_kn
            else:
                # 如果没有返回分数，使用降级策略
                logger.warning("关系路径重排序未返回分数，使用降级策略")
                return cls._filter_relation_paths_with_fallback(
                    query, kn_ids, network_details, all_relation_types, relation_mapping,
                    all_obj_id_to_name, top_k_per_network, top_k_total, session_id
                )
        except Exception as e:
            # 如果向量重排序调用失败，使用降级策略
            logger.error(f"关系路径重排序调用失败: {str(e)}，使用降级策略", exc_info=True)
            return cls._filter_relation_paths_with_fallback(
                query, kn_ids, network_details, all_relation_types, relation_mapping,
                all_obj_id_to_name, top_k_per_network, top_k_total, session_id
            )

    @classmethod
    def _compute_keyword_match_score(cls, text: str, query: str) -> float:
        """
        计算关键词匹配分数（降级策略）
        使用统一的分数计算方法
        """
        return UnifiedRankingUtils.compute_keyword_match_score(text, query)
    
    @classmethod
    def _filter_relation_paths_with_fallback(
        cls,
        query: str,
        kn_ids: List[str],
        network_details: Dict[str, Dict[str, Any]],
        all_relation_types: List[Dict[str, Any]],
        relation_mapping: List[Dict[str, Any]],
        all_obj_id_to_name: Dict[str, str],
        top_k_per_network: int,
        top_k_total: int,
        session_id: Optional[str] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        关系路径降级策略：使用粗召回分数或关键词匹配分数排序
        
        Args:
            query: 用户查询
            kn_ids: 知识网络ID列表
            network_details: 知识网络详情字典
            all_relation_types: 所有关系类型列表
            relation_mapping: 关系类型映射
            all_obj_id_to_name: 对象类型ID到名称的映射
            top_k_per_network: 每个知识网络选择的关系路径数量
            top_k_total: 最终选择的关系路径总数量
            session_id: 会话ID
            
        Returns:
            按知识网络ID分组的过滤后的关系类型字典
        """
        # 为每个关系类型计算分数
        scored_relations = []
        query_lower = (query or "").lower()
        query_words = set(query_lower.split()) if query_lower else set()
        
        for rel_type in all_relation_types:
            score = 0.0
            
            # 优先使用粗召回的分数
            if rel_type.get("_score") is not None:
                try:
                    score = float(rel_type.get("_score"))
                except (ValueError, TypeError):
                    score = 0.0
            
            # 如果没有粗召回分数，使用关键词匹配
            if score == 0.0:
                rel_name = (rel_type.get("name") or "").lower()
                rel_comment = (rel_type.get("comment") or "").lower()
                rel_text = f"{rel_name} {rel_comment}"
                score = cls._compute_keyword_match_score(rel_text, query)
            
            scored_relations.append((score, rel_type))
        
        # 按分数降序排序
        scored_relations.sort(key=lambda x: x[0], reverse=True)
        
        # 按知识网络分组
        grouped_relations = {}
        for score, rel_type in scored_relations:
            kn_id = rel_type.get("knowledge_network_id")
            if kn_id:
                if kn_id not in grouped_relations:
                    grouped_relations[kn_id] = []
                grouped_relations[kn_id].append((score, rel_type))
        
        # 为每个知识网络选择前 top_k_per_network 个
        selected_relations_by_kn = {}
        for kn_id in kn_ids:
            if kn_id in grouped_relations:
                relations = grouped_relations[kn_id]
                # 已经按分数排序，直接取前 top_k_per_network 个
                selected_relations_by_kn[kn_id] = [rel for _, rel in relations[:top_k_per_network]]
            elif kn_id in network_details and "relation_types" in network_details[kn_id]:
                # 如果没有分数信息，直接取前 top_k_per_network 个
                relation_types = network_details[kn_id]["relation_types"][:top_k_per_network]
                selected_relations_by_kn[kn_id] = relation_types
        
        # 如果总数超过 top_k_total，全局排序并截断
        all_selected = []
        for kn_id, relations in selected_relations_by_kn.items():
            for rel in relations:
                # 重新获取分数
                score = rel.get("_score", 0.0)
                if score == 0.0:
                    rel_name = (rel.get("name") or "").lower()
                    rel_comment = (rel.get("comment") or "").lower()
                    rel_text = f"{rel_name} {rel_comment}"
                    score = cls._compute_keyword_match_score(rel_text, query)
                all_selected.append((score, rel))
        
        if len(all_selected) > top_k_total:
            all_selected.sort(key=lambda x: x[0], reverse=True)
            all_selected = all_selected[:top_k_total]
            
            # 重新按知识网络分组
            final_selected_by_kn = {}
            for score, rel in all_selected:
                kn_id = rel.get("knowledge_network_id")
                if kn_id:
                    if kn_id not in final_selected_by_kn:
                        final_selected_by_kn[kn_id] = []
                    final_selected_by_kn[kn_id].append(rel)
            
            total_count = sum(len(relations) for relations in final_selected_by_kn.values())
            logger.debug(f"降级策略完成，使用粗召回分数/关键词匹配，返回关系路径数量: {total_count}")
            return final_selected_by_kn
        
        total_count = sum(len(relations) for relations in selected_relations_by_kn.values())
        logger.debug(f"降级策略完成，使用粗召回分数/关键词匹配，返回关系路径数量: {total_count}")
        return selected_relations_by_kn

    @classmethod
    def _format_relation_paths(cls, relation_types: List[Dict[str, Any]], obj_id_to_name: Dict[str, str]) -> str:
        """
        格式化关系类型路径，按源对象类型分组并以树形结构展示
        
        Args:
            relation_types: 关系类型列表
            obj_id_to_name: 对象类型ID到名称的映射
            
        Returns:
            格式化后的关系类型路径字符串
        """
        if not relation_types:
            return ""
            
        # 按源对象类型分组关系
        relation_groups = {}
        for rel_type in relation_types:
            # 获取源对象和目标对象名称
            source_name = obj_id_to_name.get(rel_type.get("source_object_type_id"), "未知")
            target_name = obj_id_to_name.get(rel_type.get("target_object_type_id"), "未知")
            rel_name = rel_type.get("name", rel_type.get("id", "未知"))
            
            # 按源对象类型分组
            if source_name not in relation_groups:
                relation_groups[source_name] = []
            relation_groups[source_name].append((rel_name, target_name))
        
        # 构建格式化字符串
        formatted_paths = "关系类型路径:\n"
        # 按源对象类型排序并添加到提示词
        for source_name in sorted(relation_groups.keys()):
            relations = relation_groups[source_name]
            formatted_paths += f"{source_name}\n"
            for i, (rel_name, target_name) in enumerate(relations):
                if i == len(relations) - 1:
                    formatted_paths += f"└─ {rel_name} -> {target_name}\n"
                else:
                    formatted_paths += f"├─ {rel_name} -> {target_name}\n"
        
        return formatted_paths

    @classmethod
    async def _build_knowledge_network_prompt(cls, query: str, kn_ids: List[str], 
                                             network_details: Dict[str, Dict[str, Any]], filtered_relations_by_kn: Dict[str, List[Dict[str, Any]]], additional_context: Optional[str] = None, session_id: str = None, enable_rerank: bool = True) -> tuple[str, Dict[int, str]]:
        """
        构建知识网络排序提示词
        
        Args:
            query: 用户查询
            kn_ids: 知识网络ID列表
            network_details: 知识网络详情字典
            filtered_relations_by_kn: 已过滤的关系类型（如果已提供则直接使用）
            additional_context: 额外的上下文信息
            session_id: 会话ID
            enable_rerank: 是否启用向量重排序
            
        Returns:
            (提示词, 编号到ID的映射字典)
        """
        # 构建提示词
        prompt = f"请分析以下知识网络列表，只返回与问题相关的知识网络数字编号，按相关性从高到低排序。\n\n知识网络列表:\n"
        
        # 如果未提供 filtered_relations_by_kn，则进行重排序
        if not filtered_relations_by_kn:
            filtered_relations_by_kn = await cls._filter_all_relation_paths_with_rerank(
                query, kn_ids, network_details, session_id, top_k_per_network=3, top_k_total=10, enable_rerank=enable_rerank
            )
        
        kn_mapping = {}
        for idx, kn_id in enumerate(kn_ids, 1):
            kn_mapping[idx] = kn_id
            prompt += f"{idx}. {kn_id}: {network_details[kn_id]['name']}\n   描述: {network_details[kn_id]['comment']}\n"
            
            # 添加关系类型和关联路径信息（采用分组展示方式）
            if kn_id in filtered_relations_by_kn:
                filtered_relation_types = filtered_relations_by_kn[kn_id]
                # 创建对象类型ID到名称的映射
                obj_id_to_name = {obj_type.get('id', ''): obj_type.get('name', obj_type.get('id', '')) \
                                 for obj_type in network_details[kn_id].get("object_types", [])}
                
                # 使用统一的格式化函数处理过滤后的关系类型路径
                formatted_paths = cls._format_relation_paths(filtered_relation_types, obj_id_to_name)
                if formatted_paths:
                    prompt += f"   {formatted_paths}"
            prompt += "\n"
        
        # 修改提示词中的提示内容，包含关系类型信息和额外上下文
        if additional_context:
            prompt += f"请根据以下问题、知识网络名称、对象类型和关系类型路径，以及额外的上下文信息，返回和问题可能相关的知识网络编号，按相关性排序，不要解释，以列表形式返回数字编号，例如：[2, 1, 3]，不能返回空列表[]\n\n问题: {query}\n\n额外上下文信息: {additional_context}"
        else:
            prompt += f"请根据以下问题、知识网络名称、对象类型和关系类型路径，返回和问题可能相关的知识网络编号，按相关性排序，不要解释，以列表形式返回数字编号，例如：[2, 1, 3]，不能返回空列表[]\n\n问题: {query}"
            
        formatted_prompt = "\n" + "="*50 + "\n" + "知识网络排序提示词" + "\n" + "="*50 + "\n" + prompt + "\n" + "="*50 + "\n"
        logger.info(formatted_prompt)
        
        return prompt, kn_mapping

    @classmethod
    async def _rank_knowledge_networks(
        cls,
        query: str,
        top_k: int,
        additional_context: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        session_id: str = None,
        kn_ids: List[str] = None,
        account_id: str = None,
        account_type: str = None,
        concept_config: Optional["ConceptRetrievalConfig"] = None,
        enable_rerank: bool = True,
    ) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        使用LLM对知识网络进行相关性排序，或者直接使用指定的知识网络ID列表
        
        Args:
            query: 用户查询
            top_k: 返回最相关的知识网络数量
            additional_context: 额外的上下文信息，用于二次检索时提供更精确的检索信息
            headers: HTTP请求头
            session_id: 会话ID
            kn_ids: 指定的知识网络ID列表，如果不传则检索所有知识网络
            
        Returns:
            (相关知识网络ID列表, 知识网络详情列表)
        """
            
        # 并行获取所有知识网络的详情
        network_details: Dict[str, Dict[str, Any]] = {}
        detail_tasks = [KnowledgeNetworkHTTPClient._get_knowledge_network_detail(kn, headers) for kn in kn_ids]
        detail_results = await asyncio.gather(*detail_tasks, return_exceptions=True)

        errors: Dict[str, Any] = {}
        for i, detail in enumerate(detail_results):
            kn = kn_ids[i]
            if isinstance(detail, dict):
                network_details[kn] = detail
            elif detail is not None:
                # 记录下每个知识网络的错误信息
                logger.error(f"获取知识网络详情失败 (kn_id={kn}): {str(detail)}")
                errors[kn] = str(detail)

        # 如果所有知识网络详情都获取失败，直接抛出统一的检索错误，避免后续流程继续执行
        if not network_details:
            msg = "获取业务知识网络详情接口调用失败，无法继续执行概念召回"
            logger.error(f"{msg}，kn_ids={kn_ids}, errors={errors}")
            raise KnowledgeNetworkRetrievalError(
                detail={
                    "error": msg,
                    "kn_ids": kn_ids,
                    "upstream_errors": errors,
                },
                link="https://example.com/api-docs/knowledge-network-retrieval"
            )

        # 解析概念召回配置（用于控制粗召回）
        enable_coarse = bool(getattr(concept_config, "enable_coarse_recall", False)) if concept_config else False
        coarse_obj_limit = int(getattr(concept_config, "coarse_object_limit", 2000) or 2000)
        coarse_rel_limit = int(getattr(concept_config, "coarse_relation_limit", 300) or 300)
        coarse_min_rel_count = int(getattr(concept_config, "coarse_min_relation_count", 5000) or 5000)

        # 统计当前参与排序的知识网络的关系总数，用于判断是否需要粗召回
        total_relation_count = 0
        for kn_id, detail in (network_details or {}).items():
            rel_list = (detail or {}).get("relation_types") or []
            total_relation_count += len(rel_list)

        # 可选：在“大规模关系数”场景下先做对象/关系粗召回以裁剪候选集合
        # 小规模网络（关系总数低于阈值）直接走原有精排流程，避免多余的 HTTP 调用
        if enable_coarse and kn_ids and total_relation_count >= coarse_min_rel_count:
            try:
                # 为每个知识网络并发执行粗召回
                async def _run_coarse(kn: str):
                    obj_entries, rel_entries = await asyncio.gather(
                        KnowledgeNetworkHTTPClient.coarse_recall_object_types(
                            kn, query, limit=coarse_obj_limit, headers=headers
                        ),
                        KnowledgeNetworkHTTPClient.coarse_recall_relation_types(
                            kn, query, limit=coarse_rel_limit, headers=headers
                        ),
                    )
                    return kn, obj_entries, rel_entries

                coarse_results = await asyncio.gather(*[_run_coarse(kn) for kn in kn_ids])

                for kn_id, obj_entries, rel_entries in coarse_results:
                    if kn_id not in network_details:
                        continue
                    kn_detail = network_details[kn_id] or {}

                    # 关系候选集合（用于限制后续向量重排的规模）
                    rel_id_set = {item.get("id") for item in (rel_entries or []) if item.get("id")}
                    # 创建粗召回关系类型的分数映射（用于降级策略）
                    rel_score_map = {}
                    if rel_entries:
                        for rel_entry in rel_entries:
                            rel_id = rel_entry.get("id")
                            rel_score = rel_entry.get("_score")
                            if rel_id and rel_score is not None:
                                rel_score_map[rel_id] = float(rel_score)
                    
                    if rel_id_set:
                        original_rel_types = kn_detail.get("relation_types") or []
                        pruned_rel_types = []
                        for rel in original_rel_types:
                            rel_id = rel.get("id")
                            if rel_id in rel_id_set:
                                # 如果粗召回关系类型有分数信息，保留到关系类型中
                                if rel_id in rel_score_map:
                                    rel = rel.copy()
                                    rel["_score"] = rel_score_map[rel_id]
                                pruned_rel_types.append(rel)
                        if pruned_rel_types:
                            kn_detail["relation_types"] = pruned_rel_types

                    # 对象候选集合：粗召回对象ID ∪ 剩余关系的 source/target 对象ID
                    obj_id_set = {item.get("id") for item in (obj_entries or []) if item.get("id")}
                    rel_obj_ids = set()
                    for rel in kn_detail.get("relation_types") or []:
                        sid = rel.get("source_object_type_id")
                        tid = rel.get("target_object_type_id")
                        if sid:
                            rel_obj_ids.add(sid)
                        if tid:
                            rel_obj_ids.add(tid)
                    candidate_obj_ids = obj_id_set or set()
                    candidate_obj_ids.update(rel_obj_ids)

                    if candidate_obj_ids:
                        original_obj_types = kn_detail.get("object_types") or []
                        # 创建粗召回对象类型的分数映射（如果知识网络中没有关系类型，需要保留分数信息用于后续排序）
                        obj_score_map = {}
                        if obj_entries:
                            for obj_entry in obj_entries:
                                obj_id = obj_entry.get("id")
                                obj_score = obj_entry.get("_score")
                                if obj_id and obj_score is not None:
                                    obj_score_map[obj_id] = float(obj_score)
                        
                        pruned_obj_types = []
                        for obj in original_obj_types:
                            obj_id = obj.get("id")
                            if obj_id in candidate_obj_ids:
                                # 如果粗召回对象类型有分数信息，保留到对象类型中
                                if obj_id in obj_score_map:
                                    obj = obj.copy()
                                    obj["_score"] = obj_score_map[obj_id]
                                pruned_obj_types.append(obj)
                        
                        if pruned_obj_types:
                            kn_detail["object_types"] = pruned_obj_types

                    network_details[kn_id] = kn_detail
            except Exception as e:
                # 粗召回失败不影响主流程，记录日志后回退为原始 full schema
                logger.warning(
                    "粗召回候选裁剪失败，将继续使用完整schema进行重排: %s", str(e), exc_info=True
                )

        # 一次性对所有知识网络的关系路径进行向量重排序（此时 network_details 可能已被粗召回裁剪）
        filtered_relations_by_kn = await cls._filter_all_relation_paths_with_rerank(
            query,
            kn_ids,
            network_details,
            session_id,
            top_k_per_network=3,
            top_k_total=10,
            enable_rerank=enable_rerank
        )
        # 如果kn_ids的长度为1，直接返回该知识网络
        if len(kn_ids) == 1:
            kn_id = kn_ids[0]
            if kn_id in network_details:
                return network_details[kn_id]
            else:
                # 理论上前面已经在全失败场景抛错，这里只是兜底保护
                msg = f"知识网络 {kn_id} 的详情获取失败，无法执行概念召回"
                logger.error(msg)
                raise KnowledgeNetworkRetrievalError(
                    detail={"error": msg, "kn_id": kn_id},
                    link="https://example.com/api-docs/knowledge-network-retrieval"
                )
        
        
        # 如果没有提供kn_ids或只有一个ID，使用LLM进行检索
        try:
            # 构建提示词
            prompt, kn_mapping = await cls._build_knowledge_network_prompt(query, kn_ids, network_details, filtered_relations_by_kn, additional_context, session_id)
            
            # 调用LLM并获取结果
            system_message = "你是一个智能知识网络筛选助手。你能够根据用户提出的问题，从知识网络列表中筛选出相关的知识网络，并按照相关性进行排序，只返回相关知识网络的编号。"
            error_context = "上一次的回答为空或格式不正确，请重新分析问题并严格按照要求返回数字编号列表，例如：[2, 1, 3]，务必选择一个可能相关的知识网络编号，无论如何不能返回空列表[]。"
            
            content = await LLMClient.call_llm_with_retry(prompt, system_message, query, error_context, account_id=account_id, account_type=account_type)
            logger.info(f"LLM返回原始结果: {content}")
            
            # 解析LLM返回的结果
            import re
            match = re.search(r'\[([0-9,\s]+)\]', content)
            if match:
                indices_str = match.group(1)
                indices = [int(i.strip()) for i in indices_str.split(',') if i.strip().isdigit()]
                # 转换为知识网络ID
                kn_ids = [kn_mapping[idx] for idx in indices if idx in kn_mapping]
                # 只返回最相关的一个知识网络详情
                if kn_ids:  # 确保不是空列表
                    first_kn_id = kn_ids[0]
                    return network_details[first_kn_id]
            
            # 如果没有找到明确的列表或结果为空，返回
            logger.debug(f"LLM返回结果无效，返回空列表")
            return {}
                
        except Exception as e:
            logger.error(f"知识网络排序失败: {str(e)}", exc_info=True)
            # 出错时返回空
            return {}