# -*- coding: utf-8 -*-
"""
基于知识网络的概念检索模块
专注于关系类型和对象类型的检索逻辑
"""

import json
import os
import time
from typing import List, Dict, Any, Optional, Tuple, Union
from fastapi import Body, HTTPException, Header, Depends
from pydantic import BaseModel, Field
import asyncio
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict

# 导入LLM客户端
from ...infra.clients.llm_client import LLMClient
# 导入日志模块
from data_retrieval.logs.logger import logger
# 导入重排序客户端
from data_retrieval.tools.graph_tools.driven.external.rerank_client import RerankClient
# 导入标准错误响应类
from data_retrieval.errors import ErrorResponse
# 导入会话管理器
from ...services.session.session_manager import RetrievalSessionManager
# 导入统一排序工具
from ...infra.utils.ranking_utils import UnifiedRankingUtils, RankingStrategy


class ConceptRetrieval:
    """基于知识网络的概念检索工具"""
    
    def __init__(self):
        pass

    @classmethod
    def _build_network_info_prompt(cls, network_details: Dict[str, Any]) -> str:
        """
        构建提示词的网络信息部分
        
        Args:
            network_details: 知识网络详情字典
            
        Returns:
            str: 网络信息提示词
        """
        prompt = ""
        
        # 在提示词开头添加当前知识网络的名称和描述
        if network_details:
            prompt += "当前知识网络信息:\n"
            kn_id = network_details.get("id")
            kn_name = network_details.get("name", "")
            kn_comment = network_details.get("comment", "")
            prompt += f"- ID: {kn_id}, 名称: {kn_name}, 描述: {kn_comment}\n"
            prompt += "\n"
        
        return prompt
    
    @classmethod
    def _collect_relation_and_object_types(cls, network_details: Dict[str, Any], session_id: Optional[str] = None, top_k: int = 10) -> Tuple[List, List, Dict, List]:
        """
        收集所有关系类型和对象类型
        
        Args:
            network_details: 知识网络详情字典
            session_id: 会话ID，用于缓存管理
            
        Returns:
            tuple: (all_relation_types, all_object_types, objects_mapping, relations_mapping)
        """
        # 从network_details中获取kn_id
        kn_id = network_details.get("id")
        
        # 收集所有关系类型
        all_relation_types = []
        if "relation_types" in network_details:
            all_relation_types.extend(network_details["relation_types"])
        
        if not all_relation_types:
            # 如果没有关系类型，直接收集所有对象类型
            all_object_types = []
            objects_mapping = {}
            obj_idx = 1
            if "object_types" in network_details:
                for obj_type in network_details["object_types"]:
                    all_object_types.append(obj_type)
                    # 获取data_properties，确保是列表
                    data_properties = obj_type.get("data_properties", [])
                    if not isinstance(data_properties, list):
                        data_properties = []
                    logic_props = obj_type.get("logic_properties", [])
                    if not isinstance(logic_props, list):
                        logic_props = []
                    objects_mapping[obj_idx] = {
                        "id": obj_type["id"],
                        "name": obj_type["name"],
                        "comment": obj_type.get("comment", ""),
                        "kn_id": obj_type.get("kn_id", ""),
                        "data_properties": data_properties,  # 添加属性信息
                        "logic_properties": logic_props,  # 添加逻辑属性
                        "primary_keys": obj_type.get("primary_keys", []),  # 主键列表（重要字段）
                        "display_key": obj_type.get("display_key")  # 显示字段名（重要字段）
                    }
                    obj_idx += 1
            relations_mapping = []
        else:
            # 创建对象类型ID到名称的映射
            obj_id_to_name = {}
            if "object_types" in network_details:
                for obj_type in network_details["object_types"]:
                    obj_id_to_name[obj_type.get('id')] = obj_type.get('name', obj_type.get('id'))
            
            # 从会话管理器中获取所有关系路径的分数，并取前top_k个
            # 分数结果已经在 _filter_relation_paths_with_rerank 方法中保存到会话管理器中
            scored_relations = []
            for rel_type in all_relation_types:
                relation_id = rel_type.get('id')
                score = 0.0  # 默认分数
                if session_id and kn_id and relation_id:
                    cached_score = RetrievalSessionManager.get_relation_score(session_id, kn_id, relation_id)
                    if cached_score is not None:
                        score = cached_score
                scored_relations.append((score, rel_type))
            
            # 按分数降序排序并取前top_k个
            sorted_relations = cls._sort_by_score_desc(scored_relations, score_field=0)
            relations_mapping = [rel_type for score, rel_type in sorted_relations[:top_k]]
            
            # 根据这top_k条关系的源对象和目标对象，过滤掉无关的对象类型
            # 收集相关的对象类型ID
            relevant_object_type_ids = set()
            for rel_type in relations_mapping:
                relevant_object_type_ids.add(rel_type.get("source_object_type_id"))
                relevant_object_type_ids.add(rel_type.get("target_object_type_id"))
            
            # 收集过滤后的对象类型
            all_object_types = []
            objects_mapping = {}
            obj_idx = 1
            if "object_types" in network_details:
                for obj_type in network_details["object_types"]:
                    # 只保留与关系类型相关的对象类型
                    if obj_type["id"] in relevant_object_type_ids:
                        all_object_types.append(obj_type)
                        # 获取data_properties，确保是列表
                        data_properties = obj_type.get("data_properties", [])
                        if not isinstance(data_properties, list):
                            data_properties = []
                        logic_props = obj_type.get("logic_properties", [])
                        if not isinstance(logic_props, list):
                            logic_props = []
                        objects_mapping[obj_idx] = {
                            "id": obj_type["id"],
                            "name": obj_type["name"],
                            "comment": obj_type.get("comment", ""),
                            "kn_id": obj_type.get("kn_id", ""),
                            "data_properties": data_properties,  # 添加属性信息
                            "logic_properties": logic_props,  # 添加逻辑属性
                            "primary_keys": obj_type.get("primary_keys", []),  # 主键列表（重要字段）
                            "display_key": obj_type.get("display_key")  # 显示字段名（重要字段）
                        }
                        obj_idx += 1
        
        return objects_mapping, relations_mapping
    
    @classmethod
    def _build_relation_paths_prompt(cls, relations_mapping: List, objects_mapping: Dict) -> str:
        """
        构建提示词的关系路径部分，现在将关系作为编号，对象类型作为提示信息
        
        Args:
            relations_mapping: 关系类型列表
            objects_mapping: 对象映射
            
        Returns:
            str: 关系路径提示词
        """
        # 创建从对象类型ID到名称的映射
        obj_id_to_name = {obj_info['id']: obj_info['name'] for _, obj_info in objects_mapping.items()}
        
        # 构建关系编号提示词
        prompt = "关系类型编号:\n"
        for idx, rel_type in enumerate(relations_mapping, 1):
            source_obj_name = obj_id_to_name.get(rel_type.get('source_object_type_id', ''), '未知对象')
            target_obj_name = obj_id_to_name.get(rel_type.get('target_object_type_id', ''), '未知对象')
            rel_name = rel_type.get('name', '未知关系')
            prompt += f"{idx}. {source_obj_name} -> {rel_name} -> {target_obj_name}\n"
        
        prompt += "\n"
        return prompt
    
    @classmethod
    async def _call_llm_and_process_results(cls, prompt: str, query: str, objects_mapping: Dict, top_k: int, relations_mapping: List[Dict[str, Any]], account_id: str = None, account_type: str = None) -> Tuple[Dict, List[Dict[str, Any]]]:
        """
        调用LLM并处理结果，现在处理关系编号而非对象类型编号
        
        Args:
            prompt: 提示词
            query: 用户查询
            objects_mapping: 对象映射
            top_k: 返回前K个相关关系类型
            relations_mapping: 关系类型列表
            
        Returns:
            过滤后的objects_mapping和relations_mapping
        """
        try:
            # 调用LLM并获取结果
            system_message = "你是一个智能关系类型筛选助手。你能够根据用户提出的问题，从关系类型列表中筛选出相关的类型，返回相关关系类型的编号，不确定的关系务必返回，要求很高的召回率，遗漏后果很严重。"
            error_context = "上一次的回答为空或格式不正确，请重新分析问题并严格按照要求返回关系类型编号列表，例如：[2, 1, 3]。"
            
            content = await LLMClient.call_llm_with_retry(prompt, system_message, query, error_context, account_id=account_id, account_type=account_type)
            logger.info(f"LLM返回原始结果: {content}")
            
            # 解析LLM返回的结果
            import re
            match = re.search(r'\[([0-9,\s]+)\]', content)
            if match:
                indices_str = match.group(1)
                indices = [int(i.strip()) for i in indices_str.split(',') if i.strip().isdigit()]
                # 返回相关的关系类型信息
                relevant_relations = []
                for idx in indices:
                    # 检查是否为有效的关系索引（1-10）
                    if 1 <= idx <= len(relations_mapping):
                        relevant_relations.append(relations_mapping[idx-1])
                # 应用top_k切片过滤
                if relevant_relations:  # 确保不是空列表
                    relevant_relations = relevant_relations[:top_k]
            else:
                # 如果没有找到明确的列表或结果为空，返回所有关系类型（应用top_k限制）
                logger.debug(f"LLM返回结果无效，返回所有关系类型")
                relevant_relations = relations_mapping[:top_k]
                
        except Exception as e:
            logger.error(f"关系类型排序失败: {str(e)}")
            # 出错时返回所有关系类型（应用top_k限制）
            relevant_relations = relations_mapping[:top_k]
        
        # 根据过滤后的关系类型，过滤objects_mapping
        filtered_objects_mapping = {}
        relevant_obj_ids = set()
        
        # 收集相关关系中涉及的对象类型ID
        for rel in relevant_relations:
            source_id = rel.get('source_object_type_id')
            target_id = rel.get('target_object_type_id')
            if source_id:
                relevant_obj_ids.add(source_id)
            if target_id:
                relevant_obj_ids.add(target_id)
        
        # 过滤objects_mapping，只保留相关的对象类型
        for idx, obj_info in objects_mapping.items():
            if obj_info.get('id') in relevant_obj_ids:
                filtered_objects_mapping[idx] = obj_info
        
        return filtered_objects_mapping, relevant_relations
    
    @classmethod
    def _merge_coarse_recall_objects_as_fallback(
        cls,
        filtered_objects_mapping: Dict[int, Dict[str, Any]],
        objects_mapping: Dict[int, Dict[str, Any]],
        network_details: Dict[str, Any],
        actual_relation_count: int,
        top_k: int,
    ) -> Dict[int, Dict[str, Any]]:
        """
        合并粗召回的对象类型作为兜底机制
        
        当从关系类型中提取的对象类型可能不完整时，补充粗召回的对象类型（按分数排序）
        注意：对象类型数量上限根据实际关系类型数量动态计算，为 max(实际关系数量 * 2, top_k)
        这样可以确保即使关系类型数量较少，也能有足够的对象类型；同时避免关系类型很少时返回过多对象类型
        
        Args:
            filtered_objects_mapping: 从关系类型中提取的对象类型映射
            objects_mapping: 完整的对象类型映射
            network_details: 知识网络详情（包含粗召回的对象类型分数信息）
            actual_relation_count: 实际的关系类型数量（LLM过滤后的数量）
            top_k: 关系类型数量上限，用于计算对象类型上限的下限
            
        Returns:
            合并后的对象类型映射
        """
        # 对象类型数量上限：根据实际关系类型数量动态计算
        # 使用 max(实际关系数量 * 2, top_k) 确保：
        # 1. 如果关系类型数量较多，上限为 实际关系数量 * 2
        # 2. 如果关系类型数量较少（如只有1-2个），至少保证 top_k 个对象类型
        max_object_count = max(actual_relation_count * 2, top_k)
        
        # 如果已经有足够的对象类型，不需要补充
        if len(filtered_objects_mapping) >= max_object_count:
            return filtered_objects_mapping
        
        # 收集已包含的对象类型ID
        included_obj_ids = {obj_info.get("id") for obj_info in filtered_objects_mapping.values()}
        
        # 从network_details中获取粗召回的对象类型（有_score字段的）
        coarse_recall_objects = []
        if "object_types" in network_details:
            for obj_type in network_details["object_types"]:
                obj_id = obj_type.get("id")
                obj_score = obj_type.get("_score")
                # 只考虑有分数且不在已包含列表中的对象类型
                if obj_id and obj_score is not None and obj_id not in included_obj_ids:
                    # 从objects_mapping中找到对应的对象信息
                    for idx, obj_info in objects_mapping.items():
                        if obj_info.get("id") == obj_id:
                            coarse_recall_objects.append((float(obj_score), idx, obj_info))
                            break
        
        # 按分数降序排序
        coarse_recall_objects.sort(key=lambda x: x[0], reverse=True)
        
        # 补充粗召回的对象类型（取前remaining_count个，但不超过剩余位置）
        remaining_count = max_object_count - len(filtered_objects_mapping)
        if remaining_count > 0 and coarse_recall_objects:
            for score, idx, obj_info in coarse_recall_objects[:remaining_count]:
                filtered_objects_mapping[idx] = obj_info
            logger.debug(
                f"补充粗召回对象类型作为兜底：已包含{len(included_obj_ids)}个，补充{min(remaining_count, len(coarse_recall_objects))}个，"
                f"上限={max_object_count}（实际关系数量={actual_relation_count}，top_k={top_k}）"
            )
        
        return filtered_objects_mapping
    
    @classmethod
    async def _process_object_properties(cls, objects_mapping: Dict[int, Dict[str, Any]], query: str = "", session_id: Optional[str] = None, kn_id: Optional[str] = None, enable_rerank: bool = True) -> Dict[int, Dict[str, Any]]:
        """
        处理对象属性信息，计算属性相关性分数（使用统一排序接口）
        
        Args:
            objects_mapping: 对象类型映射
            query: 用户查询，用于计算属性相关性分数
            session_id: 会话ID，用于缓存管理
            kn_id: 知识网络ID，用于缓存管理
            enable_rerank: 是否启用向量重排序
            
        Returns:
            property_mapping: 属性到对象类型的映射，包含分数信息
        """
        property_mapping = {}  # 映射属性到对象类型
        prop_idx = 0
        
        # 按对象类型分组处理属性
        for idx, obj_info in objects_mapping.items():
            obj_name = obj_info.get("name", "")  # 获取对象名称
            obj_id = obj_info.get("id")
            primary_keys = obj_info.get("primary_keys", [])  # 主键列表
            display_key = obj_info.get("display_key")  # 显示字段名
            
            if not obj_info.get("data_properties"):
                continue
            
            # 收集该对象类型的所有属性
            properties = []
            prop_idx_to_prop = {}  # 属性索引到属性的映射
            
            for prop in obj_info["data_properties"]:
                prop_name = prop.get("display_name") or prop.get("name", "")
                if not prop_name:
                    continue
                
                # 构建属性字典（包含完整信息）
                prop_dict = {
                    "name": prop.get("name", ""),
                    "display_name": prop_name,
                    "comment": prop.get("comment", ""),
                    "prop_idx": prop_idx,
                }
                properties.append(prop_dict)
                prop_idx_to_prop[prop_idx] = prop_dict
                
                # 初始化 property_mapping
                property_mapping[prop_idx] = {
                    "obj_idx": idx,
                    "prop_name": prop_name,
                    "prop_comment": prop.get("comment", ""),
                    "obj_id": obj_id,
                    "score": 0.0
                }
                
                # 检查缓存
                if session_id and kn_id and obj_id and prop_name:
                    cached_score = RetrievalSessionManager.get_property_score(
                        session_id, kn_id, f"{obj_id}_{prop_name}"
                    )
                    if cached_score is not None:
                        property_mapping[prop_idx]["score"] = cached_score
                        prop_dict["semantic_score"] = cached_score
                
                prop_idx += 1
            
            # 如果有查询且存在未缓存的属性，使用统一排序接口
            if query and properties:
                # 找出未缓存的属性
                uncached_properties = [
                    p for p in properties 
                    if p.get("semantic_score") is None
                ]
                
                if uncached_properties:
                    # 使用统一排序接口
                    strategy = RankingStrategy.RERANK if enable_rerank else RankingStrategy.KEYWORD_MATCH
                    ranked_properties = await UnifiedRankingUtils.rank_properties(
                        properties=uncached_properties,
                        object_name=obj_name,
                        query=query,
                        enable_rerank=enable_rerank,
                        strategy=strategy,
                        primary_keys=primary_keys,
                        display_key=display_key,
                    )
                    
                    # 更新分数和缓存
                    for prop_with_score in ranked_properties:
                        prop_idx_local = prop_with_score.get("prop_idx")
                        if prop_idx_local is None or prop_idx_local not in property_mapping:
                            continue
                        
                        score = prop_with_score.get("semantic_score", 0.0)
                        prop_name = prop_with_score.get("display_name") or prop_with_score.get("name", "")
                        
                        # 更新 property_mapping
                        property_mapping[prop_idx_local]["score"] = score
                        
                        # 更新缓存
                        if obj_id and prop_name:
                            prop_key = f"{obj_id}_{prop_name}"
                            if session_id and kn_id:
                                RetrievalSessionManager.add_property_score(session_id, kn_id, prop_key, score)
                            elif kn_id:
                                # 使用临时 session_id 存储
                                temp_session_id = f"_temp_property_scores_{kn_id}"
                                RetrievalSessionManager.add_property_score(temp_session_id, kn_id, prop_key, score)
        
        total_props = len(property_mapping)
        logger.debug(f"对象属性处理完成，共处理 {total_props} 个属性")
        return property_mapping
    
    @classmethod
    def _filter_and_group_properties(
        cls,
        property_mapping: Dict[int, Dict[str, Any]],
        per_object_top_k: int = 3,
        global_top_k: int = 10,
    ) -> Tuple[List[Dict[str, Any]], Dict[int, List[Dict[str, Any]]]]:
        """
        按对象类型分组并筛选属性
        
        Args:
            property_mapping: 属性到对象类型的映射，包含分数信息
            objects_mapping: 对象类型映射
            
        Returns:
            final_candidate_props: 最终候选属性列表
            obj_type_props: 按对象类型分组的属性
        """
        # 首先，为所有属性获取分数
        all_props_with_scores = []
        for prop_idx, mapping_info in property_mapping.items():
            score = mapping_info.get("score", 0.0)
            obj_idx = mapping_info["obj_idx"]
            prop_info = {
                "name": mapping_info["prop_name"],
                "comment": mapping_info["prop_comment"],
                "score": score,
                "obj_idx": obj_idx
            }
            all_props_with_scores.append(prop_info)
        
        # 按对象类型分组并为每个对象类型取前 per_object_top_k 个属性
        obj_type_props = {}
        for prop_info in all_props_with_scores:
            obj_idx = prop_info["obj_idx"]
            if obj_idx not in obj_type_props:
                obj_type_props[obj_idx] = []
            obj_type_props[obj_idx].append(prop_info)
        
        # 对每个对象类型的属性按分数排序，并取前 per_object_top_k 个
        for obj_idx, props in obj_type_props.items():
            props.sort(key=lambda x: x["score"], reverse=True)
            # 每个对象类型只保留前 per_object_top_k 个属性（至少为1）
            top_n = max(int(per_object_top_k or 1), 1)
            obj_type_props[obj_idx] = props[:top_n]
        
        # 将所有对象类型的前 per_object_top_k 个属性合并到一个列表中
        all_top_props = []
        for obj_idx, props in obj_type_props.items():
            all_top_props.extend(props)
        
        # 对合并后的属性按分数排序
        all_top_props.sort(key=lambda x: x["score"], reverse=True)
        
        # 取前 global_top_k 个作为最终的候选属性（至少为1）
        g_top = max(int(global_top_k or 1), 1)
        final_candidate_props = all_top_props[:g_top]
        
        # 改进错误处理和日志记录
        logger.debug(f"属性处理完成，共处理 {len(all_props_with_scores)} 个属性，最终候选属性数量: {len(final_candidate_props)}")
        
        return final_candidate_props, obj_type_props
    
    @classmethod
    def _build_object_types_detail_prompt(cls, objects_mapping: Dict[int, Dict[str, Any]], 
                                        obj_type_props: Dict[int, List[Dict[str, Any]]], 
                                        final_candidate_props: List[Dict[str, Any]]) -> str:
        """
        构建对象类型详细信息提示词部分
        
        Args:
            objects_mapping: 对象类型映射
            obj_type_props: 按对象类型分组的属性
            final_candidate_props: 最终候选属性列表
            
        Returns:
            prompt: 对象类型详细信息提示词部分
        """
        if not objects_mapping:
            logger.debug("对象类型映射为空，返回空字符串")
            return ""
        
        prompt = "对象类型详细信息:\n"
        for idx, obj_info in objects_mapping.items():
            # 去掉编号，只显示名称
            prompt += f"{obj_info['name']}\n"
            # 添加属性信息，只显示最终候选属性中的属性
            if idx in obj_type_props:
                props = obj_type_props[idx]
                # 过滤出在最终候选属性中的属性
                filtered_props = [prop for prop in props if prop in final_candidate_props]
                # 添加该对象类型的属性到提示词中
                if filtered_props:
                    prompt += "   属性:\n"
                    for prop in filtered_props:
                        if prop["comment"]:
                            prompt += f"     - {prop['comment']}\n"
                        else:
                            prompt += f"     - {prop['name']}\n"
            prompt += "\n"
            
        logger.debug(f"构建对象类型详细信息提示词完成，共 {len(objects_mapping)} 个对象类型")
        return prompt
    
    @classmethod
    def _build_context_and_finalize_prompt(cls, prompt: str, query: str, additional_context: Optional[str], 
                                         session_id: Optional[str], objects_mapping: Dict[int, Dict[str, Any]], 
                                         current_kn_id: Optional[str] = None) -> str:
        """
        构建上下文和历史记录信息并完善提示词
        
        Args:
            prompt: 当前提示词
            query: 用户查询
            additional_context: 额外上下文信息
            session_id: 会话ID
            objects_mapping: 对象类型映射
            current_kn_id: 当前知识网络ID
            
        Returns:
            完整的提示词
        """
        context_info = ""
        history_info = ""
        
        # 处理额外上下文信息
        if additional_context:
            context_info += f"\n额外上下文信息: {additional_context}"
            logger.debug("添加额外的上下文信息")
            
        # 添加历史召回记录信息（如果有会话ID）
        if session_id and current_kn_id:
            retrieved_concept_ids = RetrievalSessionManager.get_retrieved_concept_ids(session_id, current_kn_id)
            if retrieved_concept_ids:
                history_info = "\n历史召回记录（请避免重复召回这些已召回的概念）:\n"
                
                # 按轮次组织记录
                round_records = {}
                for record in retrieved_concept_ids:
                    concept_id = record.get("concept_id", "")
                    concept_name = record.get("concept_name", "")
                    concept_type = record.get("concept_type", "")
                    
                    # 记录信息（简化显示格式）
                    # 由于对象类型不再有编号，所以不再显示编号
                    record_info = f"{concept_name}"
                    
                    # 添加到轮次记录中
                    if "round" not in record:
                        # 如果没有轮次信息，按顺序分配轮次
                        round_num = len(round_records) + 1
                    else:
                        round_num = record["round"]
                    
                    if round_num not in round_records:
                        round_records[round_num] = []
                    round_records[round_num].append(record_info)
                
                # 按轮次显示记录，最多只显示最近5轮
                sorted_rounds = sorted(round_records.keys(), reverse=True)
                displayed_rounds = sorted_rounds[:5]  # 只显示最近5轮
                
                for round_num in sorted(displayed_rounds):
                    history_info += f"  第{round_num}轮: {', '.join(round_records[round_num])}\n"
                
                if len(sorted_rounds) > 5:
                    history_info += f"  ... (还有{len(sorted_rounds) - 5}轮记录)\n"
                
                if history_info != "\n历史召回记录（请避免重复召回这些已召回的概念）:\n":  # 确保有实际内容
                    context_info += history_info
                    logger.debug(f"添加历史记录信息，共 {len(displayed_rounds)} 条记录")
                else:
                    logger.debug("历史记录信息为空")
            else:
                logger.debug("上下文信息为空")
        
        # 完善提示词，现在要求返回相关的关系编号而非对象类型编号
        if history_info:
            prompt += f"\n请根据以下问题、对象类型信息和关系类型编号{context_info}\n根据以上信息判断还有哪些关系类型编号和问题相关，却没有召回，不要解释，以列表形式返回，例如：[2, 1, 3]，之前召回的概念有缺失，请务必召回新的关系类型编号，只要有一点点可能相关即可。\n\n问题: {query}"
        else:
            prompt += f"\n请根据以下问题，并结合对象类型信息和关系类型编号{context_info}\n，判断问题涉及的子图信息，并只返回子图涉及的关系类型编号，不要解释，以列表形式返回，例如：[2, 1, 3]，都不相关则返回[]，如果不确定或只要一点点相关，就返回，不要遗漏任何关系类型\n\n问题: {query}"
            
        logger.debug("提示词完善完成")
        return prompt

    @classmethod
    def _sort_by_score_desc(cls, items: List[Any], score_field: Union[str, int] = "score") -> List[Any]:
        """
        按分数降序排列对象列表
        
        Args:
            items: 包含分数字段的对象列表，可以是字典列表或元组列表
            score_field: 分数字段名（字典）或索引（元组），默认为"score"
            
        Returns:
            按分数降序排列的对象列表
        """
        if not items:
            return items
            
        # 判断是字典列表还是元组列表
        if isinstance(items[0], dict):
            # 字典列表情况
            return sorted(items, key=lambda x: x.get(score_field, 0), reverse=True)
        elif isinstance(items[0], (tuple, list)):
            # 元组或列表情况，假设分数在指定索引位置
            return sorted(items, key=lambda x: x[score_field] if len(x) > score_field else 0, reverse=True)
        else:
            # 其他情况，尝试直接访问属性
            return sorted(items, key=lambda x: getattr(x, score_field, 0), reverse=True)
    
    @classmethod
    async def rank_relation_types(
        cls,
        query: str,
        network_details: Dict[str, Any],
        top_k: int = 10,
        additional_context: Optional[str] = None,
        session_id: Optional[str] = None,
        skip_llm: bool = False,
        account_id: str = None,
        account_type: str = None,
        per_object_property_top_k: int = 8,
        global_property_top_k: int = 30,
        enable_rerank: bool = True,
    ) -> Tuple[Dict, List[Dict[str, Any]]]:
        """
        使用LLM对关系类型进行相关性排序
        
        Args:
            query: 用户查询
            network_details: 知识网络详情字典
            top_k: 返回前K个相关关系类型，默认为10
            additional_context: 额外的上下文信息，用于二次检索时提供更精确的检索信息
            session_id: 会话ID，用于获取历史召回记录
            skip_llm: 是否跳过LLM处理，直接返回前top_k个关系类型，默认为False
            
        Returns:
            过滤后的objects_mapping和relations_mapping
        """
        if not network_details:
            return {}, []
            
        # 1. 初始化和数据收集
        current_kn_id = network_details.get('id')
        # 收集top_k个关系类型和对象类型
        objects_mapping, relations_mapping = cls._collect_relation_and_object_types(
            network_details, session_id, top_k)
        
        # 3. 处理对象属性信息（即便跳过LLM也要打分，供后续schema裁剪使用）
        try:
            property_mapping = await cls._process_object_properties(objects_mapping, query, session_id, current_kn_id, enable_rerank=enable_rerank)
        except Exception as e:
            logger.warning(f"对象属性打分失败，将跳过属性分数缓存: {e}", exc_info=True)
            property_mapping = {}

        # 场景A：知识网络中没有任何关系类型，仅返回对象类型（支持"只关心对象schema"的场景）
        if not relations_mapping:
            if objects_mapping:
                # 如果对象类型有分数信息（来自粗召回），按分数排序并取前top_k*2个
                # 注意：对象类型数量上限为 top_k * 2，因为每个关系类型涉及2个对象类型（source和target）
                max_object_count = top_k * 2
                objects_with_scores = []
                objects_without_scores = []
                
                for idx, obj_info in objects_mapping.items():
                    # 从network_details中获取对象类型的_score字段
                    obj_id = obj_info.get("id")
                    obj_score = None
                    if "object_types" in network_details:
                        for obj_type in network_details["object_types"]:
                            if obj_type.get("id") == obj_id:
                                obj_score = obj_type.get("_score")
                                break
                    
                    if obj_score is not None:
                        objects_with_scores.append((float(obj_score), idx, obj_info))
                    else:
                        objects_without_scores.append((idx, obj_info))
                
                # 按分数降序排序
                objects_with_scores.sort(key=lambda x: x[0], reverse=True)
                
                # 构建最终的对象类型映射
                filtered_objects_mapping = {}
                # 先添加有分数的对象类型（按分数排序，取前max_object_count个）
                for score, idx, obj_info in objects_with_scores[:max_object_count]:
                    filtered_objects_mapping[idx] = obj_info
                
                # 如果还有剩余位置，添加没有分数的对象类型
                remaining_count = max_object_count - len(filtered_objects_mapping)
                if remaining_count > 0:
                    for idx, obj_info in objects_without_scores[:remaining_count]:
                        filtered_objects_mapping[idx] = obj_info
                
                logger.info(
                    "知识网络(id=%s) 中没有关系类型，基于粗召回对象类型分数返回前%d个对象类型（总数=%d，有分数=%d，无分数=%d）",
                    current_kn_id,
                    len(filtered_objects_mapping),
                    len(objects_mapping),
                    len(objects_with_scores),
                    len(objects_without_scores),
                )
                return filtered_objects_mapping, []
            logger.warning("知识网络(id=%s) 中既没有关系类型也没有对象类型，返回空结果", current_kn_id)
            return {}, []

        # 如果跳过LLM处理，直接返回前top_k个关系类型（但已完成属性打分）
        if skip_llm:
            logger.debug(f"跳过LLM处理，直接返回前{top_k}个关系类型（当前relations_mapping有{len(relations_mapping)}个）")
            if len(relations_mapping) > top_k:
                relations_mapping = relations_mapping[:top_k]
            
            # 根据过滤后的关系类型，过滤objects_mapping（只保留关系类型涉及的source/target对象类型）
            filtered_objects_mapping = {}
            relevant_obj_ids = set()
            
            # 收集相关关系中涉及的对象类型ID
            for rel in relations_mapping:
                source_id = rel.get('source_object_type_id')
                target_id = rel.get('target_object_type_id')
                if source_id:
                    relevant_obj_ids.add(source_id)
                if target_id:
                    relevant_obj_ids.add(target_id)
            
            # 过滤objects_mapping，只保留相关的对象类型
            for idx, obj_info in objects_mapping.items():
                if obj_info.get('id') in relevant_obj_ids:
                    filtered_objects_mapping[idx] = obj_info
            
            # 合并粗召回的对象类型作为兜底机制（按分数排序，根据实际关系类型数量动态计算上限）
            filtered_objects_mapping = cls._merge_coarse_recall_objects_as_fallback(
                filtered_objects_mapping, objects_mapping, network_details, len(relations_mapping), top_k
            )
            
            logger.debug(f"从{len(relations_mapping)}个关系类型中提取出{len(filtered_objects_mapping)}个相关对象类型（包含粗召回兜底）")
            return filtered_objects_mapping, relations_mapping

        # 4. 按对象类型分组并筛选属性（使用配置的TopK，而非写死）
        final_candidate_props, obj_type_props = cls._filter_and_group_properties(
            property_mapping,
            per_object_top_k=per_object_property_top_k,
            global_top_k=global_property_top_k,
        )
            
        # 2. 构建基础提示词
        prompt = cls._build_network_info_prompt(network_details)
        # 4. 构建对象类型详细信息（放在关系类型编号之前）
        prompt += cls._build_object_types_detail_prompt(objects_mapping, obj_type_props, final_candidate_props)
        
        # 5. 构建关系类型编号信息
        prompt += cls._build_relation_paths_prompt(relations_mapping, objects_mapping)
        
        # 6. 添加上下文和历史记录信息并完善提示词
        prompt = cls._build_context_and_finalize_prompt(prompt, query, additional_context, session_id, objects_mapping, current_kn_id)
        
        # 美化prompt并打印
        formatted_prompt = "\n" + "="*50 + "\n" + "关系类型排序提示词" + "\n" + "="*50 + "\n" + prompt + "\n" + "="*50 + "\n"
        logger.debug(formatted_prompt)
        
        # 调用LLM并处理结果
        try:
            filtered_objects_mapping, relevant_relations = await cls._call_llm_and_process_results(prompt, query, objects_mapping, top_k, relations_mapping, account_id=account_id, account_type=account_type)
            # 合并粗召回的对象类型作为兜底机制（按分数排序，根据实际关系类型数量动态计算上限）
            filtered_objects_mapping = cls._merge_coarse_recall_objects_as_fallback(
                filtered_objects_mapping, objects_mapping, network_details, len(relevant_relations), top_k
            )
            logger.debug(f"成功排序关系类型，返回 {len(relevant_relations)} 个结果，对象类型数量={len(filtered_objects_mapping)}（包含粗召回兜底）")
            return filtered_objects_mapping, relevant_relations
        except Exception as e:
            logger.error(f"关系类型排序失败: {str(e)}", exc_info=True)
            raise