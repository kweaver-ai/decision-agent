# -*- coding: utf-8 -*-
"""
统一排序工具模块
提供向量重排序、关键词匹配、启发式分数等多种排序策略的统一接口
"""

import time
from typing import List, Dict, Any, Optional, Callable, Tuple
from enum import Enum
from data_retrieval.logs.logger import logger
from data_retrieval.tools.graph_tools.driven.external.rerank_client import RerankClient


class RankingStrategy(Enum):
    """排序策略枚举"""
    RERANK = "rerank"  # 向量重排序
    KEYWORD_MATCH = "keyword_match"  # 关键词匹配
    HEURISTIC = "heuristic"  # 启发式分数
    COARSE_SCORE = "coarse_score"  # 粗召回分数


class UnifiedRankingUtils:
    """统一排序工具类"""
    
    # ============================================================
    # 1. 统一的文本构建方法
    # ============================================================
    
    @staticmethod
    def build_property_text(
        object_name: str,
        property_name: str,
        property_comment: Optional[str] = None
    ) -> str:
        """
        统一构建属性文本格式：{对象类型} 的 {属性名称}
        
        Args:
            object_name: 对象类型名称
            property_name: 属性名称
            property_comment: 属性描述（可选，用于增强语义）
            
        Returns:
            标准化的属性文本
        """
        if not object_name and not property_name:
            return ""
        
        # 标准格式：对象类型 的 属性名称
        if object_name and property_name:
            text = f"{object_name} 的 {property_name}"
            # 如果有描述，追加到后面（用逗号分隔）
            if property_comment:
                text = f"{text}，{property_comment}"
            return text
        
        # 兜底：只有属性名称
        if property_name:
            return property_name
        
        # 兜底：只有对象类型名称
        return object_name
    
    @staticmethod
    def build_relation_text(
        source_name: str,
        relation_name: str,
        target_name: str
    ) -> str:
        """
        统一构建关系路径文本格式：{源对象} {关系} {目标对象}
        
        Args:
            source_name: 源对象类型名称
            relation_name: 关系类型名称
            target_name: 目标对象类型名称
            
        Returns:
            标准化的关系路径文本
        """
        parts = []
        if source_name:
            parts.append(source_name)
        if relation_name:
            parts.append(relation_name)
        if target_name:
            parts.append(target_name)
        return " ".join(parts) if parts else ""
    
    # ============================================================
    # 2. 统一的分数计算策略
    # ============================================================
    
    @staticmethod
    def compute_keyword_match_score(text: str, query: str) -> float:
        """
        统一的关键词匹配分数计算（降级策略）
        
        规则：
        - 完全匹配：0.9
        - 关键词交集：min(0.7, 共同关键词数 / 查询关键词总数)
        - 无匹配：0.0
        
        Args:
            text: 待匹配的文本
            query: 查询文本
            
        Returns:
            匹配分数（0.0-1.0）
        """
        if not text or not query:
            return 0.0
        
        text_lower = text.lower()
        query_lower = query.lower()
        
        # 完全匹配
        if query_lower in text_lower or text_lower in query_lower:
            return 0.9
        
        # 关键词匹配
        query_words = set(query_lower.split())
        text_words = set(text_lower.split())
        common_words = query_words & text_words
        
        if common_words:
            return min(0.7, len(common_words) / len(query_words) if query_words else 0.0)
        
        return 0.0
    
    @staticmethod
    def compute_heuristic_score(
        instance_name: str,
        query: str
    ) -> float:
        """
        统一的启发式分数计算（实例排序降级策略）
        
        规则：
        - 完全相等：1.0
        - 包含关系：0.8
        - 其他：0.0
        
        Args:
            instance_name: 实例名称
            query: 查询文本
            
        Returns:
            启发式分数（0.0-1.0）
        """
        if not instance_name or not query:
            return 0.0
        
        name_lower = instance_name.lower()
        query_lower = query.lower()
        
        if name_lower == query_lower:
            return 1.0
        elif query_lower in name_lower:
            return 0.8
        else:
            return 0.0
    
    # ============================================================
    # 3. 向量重排序（内部方法）
    # ============================================================
    
    @staticmethod
    async def _rerank_texts(
        query: str,
        texts: List[str],
        batch_size: int = 128
    ) -> List[float]:
        """
        向量重排序（内部方法）
        
        Args:
            query: 查询文本
            texts: 待排序的文本列表
            batch_size: 批处理大小
            
        Returns:
            分数列表，与texts同序
        """
        if not texts:
            return []
        
        scores: List[float] = []
        client = RerankClient()
        
        logger.info(f"[向量重排序] 开始调用RerankClient.ado_rerank，texts数量={len(texts)}，batch_size={batch_size}，query长度={len(query)}")
        
        for i in range(0, len(texts), max(int(batch_size), 1)):
            batch = texts[i : i + max(int(batch_size), 1)]
            t0 = time.monotonic()
            try:
                logger.debug(f"[向量重排序] 调用RerankClient.ado_rerank，batch索引={i}，batch大小={len(batch)}")
                rerank_scores = await client.ado_rerank(batch, query)
                logger.debug(f"[向量重排序] RerankClient.ado_rerank返回，batch索引={i}，返回分数数量={len(rerank_scores) if rerank_scores else 0}")
            except Exception as e:
                logger.warning(f"向量重排序失败: {e}，使用关键词匹配降级策略")
                # 降级为关键词匹配
                batch_scores = [
                    UnifiedRankingUtils.compute_keyword_match_score(text, query)
                    for text in batch
                ]
                scores.extend(batch_scores)
                continue
            finally:
                elapsed_ms = (time.monotonic() - t0) * 1000
                try:
                    from .timing_utils import add_cost
                    add_cost("rerank", elapsed_ms)
                except Exception:
                    pass
            
            try:
                # rerank 返回格式: [{"relevance_score": 0.985, "index": 1, ...}, ...]
                # 需要根据index重新排序并提取分数
                if rerank_scores and len(rerank_scores) > 0:
                    sorted_scores = sorted(rerank_scores, key=lambda x: x.get("index", 0))
                    validated_scores = [
                        float(item["relevance_score"]) 
                        for item in sorted_scores 
                        if isinstance(item.get("relevance_score"), (int, float))
                    ]
                    
                    # 确保分数数量与batch一致
                    if len(validated_scores) == len(batch):
                        scores.extend(validated_scores)
                    elif len(validated_scores) > len(batch):
                        scores.extend(validated_scores[:len(batch)])
                    else:
                        # 如果分数数量不足，用关键词匹配补齐
                        scores.extend(validated_scores)
                        for j in range(len(validated_scores), len(batch)):
                            scores.append(
                                UnifiedRankingUtils.compute_keyword_match_score(batch[j], query)
                            )
                else:
                    # 降级为关键词匹配
                    batch_scores = [
                        UnifiedRankingUtils.compute_keyword_match_score(text, query)
                        for text in batch
                    ]
                    scores.extend(batch_scores)
            except Exception as e:
                logger.warning(f"解析rerank分数失败: {e}，使用关键词匹配降级策略")
                # 降级为关键词匹配
                batch_scores = [
                    UnifiedRankingUtils.compute_keyword_match_score(text, query)
                    for text in batch
                ]
                scores.extend(batch_scores)
        
        # 保证长度一致
        if len(scores) != len(texts):
            if len(scores) > len(texts):
                scores = scores[: len(texts)]
            else:
                scores.extend([0.0 for _ in range(len(texts) - len(scores))])
        
        return scores
    
    # ============================================================
    # 4. 统一的排序接口
    # ============================================================
    
    @staticmethod
    async def rank_items(
        items: List[Dict[str, Any]],
        query: str,
        text_builder: Callable[[Dict[str, Any]], str],
        strategy: RankingStrategy = RankingStrategy.RERANK,
        enable_rerank: bool = True,
        batch_size: int = 128,
        fallback_strategy: Optional[RankingStrategy] = None,
    ) -> List[Tuple[float, Dict[str, Any]]]:
        """
        统一的排序接口，支持多种排序策略
        
        Args:
            items: 待排序的项列表
            query: 查询文本
            text_builder: 从item构建文本的函数
            strategy: 主要排序策略
            enable_rerank: 是否启用向量重排序（当strategy=RERANK时）
            batch_size: 批处理大小（向量重排序时使用）
            fallback_strategy: 降级策略（当主策略失败时使用）
            
        Returns:
            排序后的 (分数, item) 元组列表，按分数降序
        """
        if not items or not query:
            return [(0.0, item) for item in items]
        
        # 构建文本列表
        texts = [text_builder(item) for item in items]
        
        scores: List[float] = []
        
        # 根据策略计算分数
        if strategy == RankingStrategy.RERANK and enable_rerank:
            logger.info(f"[向量重排序] rank_items使用向量重排序策略：enable_rerank=True，items数量={len(items)}")
            try:
                scores = await UnifiedRankingUtils._rerank_texts(
                    query=query,
                    texts=texts,
                    batch_size=batch_size
                )
                logger.debug(f"[向量重排序] rank_items向量重排序完成，返回{len(scores)}个分数")
            except Exception as e:
                logger.warning(f"[向量重排序] rank_items向量重排序失败: {e}，使用降级策略")
                if fallback_strategy:
                    strategy = fallback_strategy
                else:
                    strategy = RankingStrategy.KEYWORD_MATCH
        elif strategy == RankingStrategy.RERANK and not enable_rerank:
            logger.info(f"[向量重排序] rank_items：enable_rerank=False，跳过向量重排序，使用关键词匹配策略，items数量={len(items)}")
            strategy = RankingStrategy.KEYWORD_MATCH
        
        # 降级策略或直接使用
        if strategy == RankingStrategy.KEYWORD_MATCH:
            scores = [
                UnifiedRankingUtils.compute_keyword_match_score(text, query)
                for text in texts
            ]
        elif strategy == RankingStrategy.HEURISTIC:
            # 启发式分数需要从item中提取instance_name
            scores = [
                UnifiedRankingUtils.compute_heuristic_score(
                    item.get("instance_name") or item.get("name") or "",
                    query
                )
                for item in items
            ]
        elif strategy == RankingStrategy.COARSE_SCORE:
            # 粗召回分数直接从item中获取
            scores = []
            for item in items:
                score = item.get("_score")
                if score is not None:
                    try:
                        scores.append(float(score))
                    except (ValueError, TypeError):
                        scores.append(0.0)
                else:
                    scores.append(0.0)
        else:
            # 默认：全0分
            scores = [0.0] * len(items)
        
        # 配对并排序
        scored_items = [(score, item) for score, item in zip(scores, items)]
        scored_items.sort(key=lambda x: x[0], reverse=True)
        
        return scored_items
    
    # ============================================================
    # 5. 统一的属性排序接口（合并对象属性和语义属性）
    # ============================================================
    
    @staticmethod
    def _is_important_property(
        prop: Dict[str, Any],
        primary_keys: Optional[List[str]] = None,
        display_key: Optional[str] = None
    ) -> bool:
        """
        判断属性是否为重要字段（主键、display_key）
        
        Args:
            prop: 属性字典
            primary_keys: 主键列表
            display_key: 显示字段名
            
        Returns:
            是否为重要字段
        """
        prop_name = prop.get("name") or prop.get("display_name") or ""
        if not prop_name:
            return False
        
        # 检查是否是主键
        if primary_keys and prop_name in primary_keys:
            return True
        
        # 检查是否是display_key
        if display_key and prop_name == display_key:
            return True
        
        return False
    
    @staticmethod
    async def rank_properties(
        properties: List[Dict[str, Any]],
        object_name: str,
        query: str,
        enable_rerank: bool = True,
        strategy: RankingStrategy = RankingStrategy.RERANK,
        primary_keys: Optional[List[str]] = None,
        display_key: Optional[str] = None,
        batch_size: int = 128,
    ) -> List[Dict[str, Any]]:
        """
        统一的属性排序接口（合并对象属性和语义属性）
        
        重要字段（主键、display_key）会默认保留，即使分数较低。
        
        Args:
            properties: 属性列表，每个属性包含 name/display_name/comment 等字段
            object_name: 对象类型名称
            query: 查询文本
            enable_rerank: 是否启用向量重排序
            strategy: 排序策略
            primary_keys: 主键列表（重要字段，默认保留）
            display_key: 显示字段名（重要字段，默认保留）
            batch_size: 批处理大小
            
        Returns:
            排序后的属性列表，每个属性包含 semantic_score 字段
        """
        if not properties:
            return []
        
        # 分离重要字段和普通字段
        important_props: List[Dict[str, Any]] = []
        normal_props: List[Dict[str, Any]] = []
        
        for prop in properties:
            if UnifiedRankingUtils._is_important_property(prop, primary_keys, display_key):
                important_props.append(prop)
            else:
                normal_props.append(prop)
        
        # 为重要字段设置保底分数（确保它们排在前面）
        for prop in important_props:
            prop["semantic_score"] = 1.0  # 重要字段保底分数
        
        # 对普通字段进行排序
        def build_property_text(prop: Dict[str, Any]) -> str:
            prop_name = prop.get("display_name") or prop.get("name") or ""
            prop_comment = prop.get("comment") or ""
            return UnifiedRankingUtils.build_property_text(
                object_name=object_name,
                property_name=prop_name,
                property_comment=prop_comment
            )
        
        scored_normal_props = await UnifiedRankingUtils.rank_items(
            items=normal_props,
            query=query,
            text_builder=build_property_text,
            strategy=strategy,
            enable_rerank=enable_rerank,
            batch_size=batch_size,
            fallback_strategy=RankingStrategy.KEYWORD_MATCH
        )
        
        # 将分数挂载到属性上
        result: List[Dict[str, Any]] = []
        
        # 先添加重要字段（保底分数1.0，确保排在前面）
        for prop in important_props:
            prop_with_score = prop.copy()
            prop_with_score["semantic_score"] = 1.0
            result.append(prop_with_score)
        
        # 再添加排序后的普通字段
        for score, prop in scored_normal_props:
            prop_with_score = prop.copy()
            prop_with_score["semantic_score"] = score
            result.append(prop_with_score)
        
        return result
    
    # ============================================================
    # 6. 统一的关系路径排序接口
    # ============================================================
    
    @staticmethod
    async def rank_relations(
        relations: List[Dict[str, Any]],
        query: str,
        obj_id_to_name: Dict[str, str],
        enable_rerank: bool = True,
        strategy: RankingStrategy = RankingStrategy.RERANK,
        batch_size: int = 128,
    ) -> List[Tuple[float, Dict[str, Any]]]:
        """
        统一的关系路径排序接口
        
        Args:
            relations: 关系类型列表
            query: 查询文本
            obj_id_to_name: 对象类型ID到名称的映射
            enable_rerank: 是否启用向量重排序
            strategy: 排序策略
            batch_size: 批处理大小
            
        Returns:
            排序后的 (分数, 关系) 元组列表
        """
        def build_relation_text(rel: Dict[str, Any]) -> str:
            source_id = rel.get("source_object_type_id", "")
            target_id = rel.get("target_object_type_id", "")
            rel_name = rel.get("name", "")
            
            source_name = obj_id_to_name.get(source_id, "未知")
            target_name = obj_id_to_name.get(target_id, "未知")
            
            return UnifiedRankingUtils.build_relation_text(
                source_name=source_name,
                relation_name=rel_name,
                target_name=target_name
            )
        
        # 优先使用粗召回分数
        scored_relations = []
        for rel in relations:
            score = 0.0
            
            # 优先使用粗召回的分数
            if rel.get("_score") is not None:
                try:
                    score = float(rel.get("_score"))
                except (ValueError, TypeError):
                    score = 0.0
            
            # 如果没有粗召回分数，使用指定策略
            if score == 0.0:
                if strategy == RankingStrategy.COARSE_SCORE:
                    # 粗召回策略但没有分数，跳过
                    continue
                # 其他策略会在 rank_items 中处理
                scored_relations.append((score, rel))
            else:
                scored_relations.append((score, rel))
        
        # 如果有粗召回分数，直接返回
        if any(score > 0.0 for score, _ in scored_relations):
            scored_relations.sort(key=lambda x: x[0], reverse=True)
            return scored_relations
        
        # 否则使用统一排序接口
        relations_to_rank = [rel for _, rel in scored_relations]
        return await UnifiedRankingUtils.rank_items(
            items=relations_to_rank,
            query=query,
            text_builder=build_relation_text,
            strategy=strategy,
            enable_rerank=enable_rerank,
            batch_size=batch_size,
            fallback_strategy=RankingStrategy.KEYWORD_MATCH
        )

