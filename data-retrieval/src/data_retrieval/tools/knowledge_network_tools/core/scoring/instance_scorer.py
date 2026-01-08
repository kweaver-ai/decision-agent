# -*- coding: utf-8 -*-
"""
实例评分模块
实现基于用户查询的多维度实例评分和过滤
"""

from typing import List, Dict, Any, Optional, Set, Tuple
from collections import defaultdict
from data_retrieval.logs.logger import logger
from data_retrieval.tools.graph_tools.driven.external.rerank_client import RerankClient
from ...infra.utils.instance_text_builder import UNIFIED_INSTANCE_TEXT_OPTIONS, build_instance_text


class InstanceScorer:
    """实例评分器"""
    
    def __init__(
        self,
        direct_relevance_weight: float = 0.7,
        path_importance_weight: float = 0.3,
        min_direct_relevance: float = 0.3,
        min_final_score: float = 0.25,
        keep_direct_matches: bool = True,
    ):
        """
        初始化实例评分器
        
        Args:
            direct_relevance_weight: 直接相关性权重
            path_importance_weight: 路径重要性权重
            min_direct_relevance: 直接相关性最低阈值
            min_final_score: 综合分数最低阈值
            keep_direct_matches: 是否始终保留直接匹配的实例
        """
        self.direct_relevance_weight = direct_relevance_weight
        self.path_importance_weight = path_importance_weight
        self.min_direct_relevance = min_direct_relevance
        self.min_final_score = min_final_score
        self.keep_direct_matches = keep_direct_matches
        
        # 确保权重和为1
        total_weight = direct_relevance_weight + path_importance_weight
        if abs(total_weight - 1.0) > 0.01:
            logger.warning(f"权重和不为1.0（当前为{total_weight}），将自动归一化")
            self.direct_relevance_weight /= total_weight
            self.path_importance_weight /= total_weight
    
    @staticmethod
    def _build_instance_description(
        instance: Dict[str, Any],
        object_type_name: str = ""
    ) -> str:
        """
        构建实例描述文本，用于 direct_relevance 向量打分（与 rerank 阶段统一 builder）
        
        Args:
            instance: 实例信息字典（应该已经包含instance_id和instance_name）
            object_type_name: 对象类型名称
            
        Returns:
            实例描述文本
        """
        return build_instance_text(
            instance,
            object_type_name=object_type_name,
            options=UNIFIED_INSTANCE_TEXT_OPTIONS,
        )
    
    async def compute_direct_relevance_scores(
        self,
        instances: List[Dict[str, Any]],
        query: str,
        object_type_map: Dict[str, str],
        batch_size: int = 100
    ) -> Dict[str, float]:
        """
        批量计算实例的直接相关性分数
        
        Args:
            instances: 实例列表
            query: 用户查询
            object_type_map: 对象类型ID到名称的映射
            batch_size: 批处理大小
            
        Returns:
            实例ID到相关性分数的映射
        """
        if not query or not instances:
            return {}
        
        logger.info(f"开始计算 {len(instances)} 个实例的直接相关性分数")
        
        # 构建实例描述文本列表
        instance_texts = []
        instance_id_map = {}  # 索引到实例ID的映射
        
        for instance in instances:
            # 实例ID应该已经在实例中（由调用方从primary_keys提取）
            instance_id = instance.get("instance_id") or instance.get("id")
            
            if not instance_id:
                logger.debug(f"跳过没有ID的实例，实例keys: {list(instance.keys())}")
                continue
            
            object_type_id = instance.get("object_type_id", "")
            object_type_name = object_type_map.get(object_type_id, "")
            
            description = self._build_instance_description(instance, object_type_name)
            # NOTE:
            # 描述文本通常包含大量属性字段，逐条输出会造成日志刷屏与敏感信息泄露风险。
            # 如需排查构造逻辑，请在本地临时打印/断点，不在服务端日志中输出描述内容。
            
            if not description or not description.strip():
                logger.warning(
                    f"实例 {instance_id} 的描述文本为空，"
                    f"instance keys: {list(instance.keys())}, "
                    f"object_type_name: {object_type_name}"
                )
                continue
            
            instance_texts.append(description)
            instance_id_map[len(instance_texts) - 1] = instance_id
        
        if not instance_texts:
            logger.warning(
                f"没有有效的实例描述文本，"
                f"输入实例数量: {len(instances)}, "
                f"成功构建描述文本的实例数量: {len(instance_texts)}"
            )
            return {}
        
        try:
            # 批量调用Rerank服务
            rerank_client = RerankClient()
            all_scores = {}
            
            # 分批处理
            for i in range(0, len(instance_texts), batch_size):
                batch_texts = instance_texts[i:i + batch_size]
                batch_indices = list(range(i, min(i + batch_size, len(instance_texts))))
                
                logger.debug(f"处理批次 {i // batch_size + 1}，包含 {len(batch_texts)} 个实例")
                
                rerank_scores = await rerank_client.ado_rerank(batch_texts, query)
                
                if rerank_scores and len(rerank_scores) > 0:
                    # 新格式: [{"relevance_score": 0.985, "index": 1, "document": null}, ...]
                    sorted_scores = sorted(rerank_scores, key=lambda x: x["index"])
                    
                    for j, item in enumerate(sorted_scores):
                        if j < len(batch_indices):
                            idx = batch_indices[j]
                            instance_id = instance_id_map.get(idx)
                            if instance_id:
                                score = float(item.get("relevance_score", 0.0))
                                all_scores[instance_id] = score
            
            logger.info(f"直接相关性分数计算完成，共计算 {len(all_scores)} 个实例的分数")
            return all_scores
            
        except Exception as e:
            logger.warning(f"计算直接相关性分数失败: {str(e)}，返回空字典", exc_info=True)
            return {}
    
    def compute_path_importance_scores(
        self,
        instance_ids: Set[str],
        direct_match_instances: Set[str],
        overlap_instances: Set[str],
        path_centrality: Dict[str, int],
        connection_counts: Dict[str, int]
    ) -> Dict[str, float]:
        """
        计算路径重要性分数
        
        Args:
            instance_ids: 所有实例ID集合
            direct_match_instances: 直接匹配的实例ID集合
            overlap_instances: 重叠节点（连接多个查询）的实例ID集合
            path_centrality: 路径中心性（实例ID到出现次数的映射）
            connection_counts: 连接数（实例ID到连接数的映射）
            
        Returns:
            实例ID到路径重要性分数的映射
        """
        scores = {}
        
        # 归一化连接数
        max_connections = max(connection_counts.values()) if connection_counts else 1
        max_centrality = max(path_centrality.values()) if path_centrality else 1
        
        for instance_id in instance_ids:
            score = 0.0
            
            # 直接匹配：+1.0
            if instance_id in direct_match_instances:
                score += 1.0
            
            # 重叠节点：+0.8
            if instance_id in overlap_instances:
                score += 0.8
            
            # 路径中心性：+0.6 * 归一化值
            centrality = path_centrality.get(instance_id, 0)
            if centrality > 0:
                score += 0.6 * (centrality / max_centrality)
            
            # 连接数：+0.4 * 归一化值
            connections = connection_counts.get(instance_id, 0)
            if connections > 0:
                score += 0.4 * (connections / max_connections)
            
            scores[instance_id] = min(score, 1.0)  # 限制在[0, 1]范围内
        
        return scores
    
    def compute_final_scores(
        self,
        instance_ids: Set[str],
        direct_relevance_scores: Dict[str, float],
        path_importance_scores: Dict[str, float]
    ) -> Dict[str, float]:
        """
        计算综合分数
        
        Args:
            instance_ids: 所有实例ID集合
            direct_relevance_scores: 直接相关性分数
            path_importance_scores: 路径重要性分数
            
        Returns:
            实例ID到综合分数的映射
        """
        final_scores = {}
        
        for instance_id in instance_ids:
            direct_score = direct_relevance_scores.get(instance_id, 0.0)
            path_score = path_importance_scores.get(instance_id, 0.0)
            
            final_score = (
                direct_score * self.direct_relevance_weight +
                path_score * self.path_importance_weight
            )
            
            final_scores[instance_id] = final_score
        
        return final_scores
    
    def filter_instances(
        self,
        instances: List[Dict[str, Any]],
        final_scores: Dict[str, float],
        direct_relevance_scores: Dict[str, float],
        is_direct_match: Dict[str, bool],
        max_instances: Optional[int] = None
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        过滤实例，分为核心实例和上下文实例
        
        Args:
            instances: 实例列表
            final_scores: 综合分数
            direct_relevance_scores: 直接相关性分数
            is_direct_match: 是否为直接匹配的实例
            max_instances: 最大保留实例数
            
        Returns:
            (核心实例列表, 上下文实例列表)
        """
        logger.debug(
            f"开始过滤实例，输入参数："
            f"实例数量={len(instances)}, "
            f"final_scores数量={len(final_scores)}, "
            f"direct_relevance_scores数量={len(direct_relevance_scores)}, "
            f"is_direct_match数量={len(is_direct_match)}, "
            f"keep_direct_matches={self.keep_direct_matches}, "
            f"min_direct_relevance={self.min_direct_relevance}, "
            f"min_final_score={self.min_final_score}"
        )
        
        # 记录所有实例ID
        all_instance_ids = [inst.get("instance_id") or inst.get("id") for inst in instances]
        logger.debug(f"所有实例ID: {all_instance_ids}")
        logger.debug(f"final_scores中的实例ID: {list(final_scores.keys())}")
        logger.debug(f"direct_relevance_scores中的实例ID: {list(direct_relevance_scores.keys())}")
        logger.debug(f"is_direct_match中的实例ID: {list(is_direct_match.keys())}")
        
        core_instances = []
        context_instances = []
        
        # 为每个实例添加分数信息
        scored_instances = []
        for instance in instances:
            # 实例ID应该已经在实例中（由调用方从primary_keys提取）
            instance_id = instance.get("instance_id") or instance.get("id")
            
            if not instance_id:
                logger.debug(f"跳过没有ID的实例: {instance.keys()}")
                continue
            
            final_score = final_scores.get(instance_id, 0.0)
            direct_score = direct_relevance_scores.get(instance_id, 0.0)
            is_direct = is_direct_match.get(instance_id, False)
            
            logger.debug(
                f"实例 {instance_id} 的分数信息: "
                f"final_score={final_score}, "
                f"direct_score={direct_score}, "
                f"is_direct={is_direct}"
            )
            
            # 构建增强的实例信息
            enhanced_instance = instance.copy()
            enhanced_instance["scores"] = {
                "direct_relevance": direct_score,
                "final_score": final_score
            }
            enhanced_instance["source_info"] = {
                "is_direct_match": is_direct
            }
            
            scored_instances.append((final_score, direct_score, is_direct, enhanced_instance))
        
        # 排序：优先直接匹配，然后按综合分数
        scored_instances.sort(key=lambda x: (not x[2], x[0]), reverse=True)
        
        logger.debug(f"排序后的实例数量: {len(scored_instances)}")
        
        # 过滤和分类
        for final_score, direct_score, is_direct, instance in scored_instances:
            instance_id = instance.get("instance_id") or instance.get("id")
            
            logger.debug(
                f"处理实例 {instance_id}: "
                f"final_score={final_score}, "
                f"direct_score={direct_score}, "
                f"is_direct={is_direct}, "
                f"keep_direct_matches={self.keep_direct_matches}"
            )
            
            # 始终保留直接匹配的实例
            if self.keep_direct_matches and is_direct:
                logger.debug(f"实例 {instance_id} 被保留（直接匹配且keep_direct_matches=True）")
                core_instances.append(instance)
                continue
            
            # 不再按分数阈值过滤（不同模型分数范围差异较大，阈值不可比）：
            # - 分数仅用于排序
            # - 最终结果只按数量Top-K硬截断（由调用方在输出阶段控制）
            
            # 分类：高分数为核心实例，较低分数为上下文实例
            if final_score >= 0.5 or is_direct:
                logger.debug(f"实例 {instance_id} 被分类为核心实例（final_score={final_score} >= 0.5 或 is_direct={is_direct}）")
                core_instances.append(instance)
            else:
                logger.debug(f"实例 {instance_id} 被分类为上下文实例（final_score={final_score} < 0.5 且 is_direct={is_direct}）")
                context_instances.append(instance)
        
        # 如果设置了最大数量，进行截断
        if max_instances is not None:
            if len(core_instances) > max_instances:
                # 保留前max_instances个核心实例
                core_instances = core_instances[:max_instances]
                # 剩余的移到上下文实例
                context_instances = scored_instances[len(core_instances):]
                context_instances = [inst for _, _, _, inst in context_instances]
        
        # 这里的“未进入输出”的主要原因通常是实例缺少ID等基础字段被跳过（不是分数阈值过滤）。
        filtered_count = len(instances) - len(core_instances) - len(context_instances)
        logger.info(
            f"实例过滤完成：核心实例 {len(core_instances)} 个，"
            f"上下文实例 {len(context_instances)} 个，"
            f"跳过 {filtered_count} 个"
        )
        
        return core_instances, context_instances

