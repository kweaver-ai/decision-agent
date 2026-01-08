# -*- coding: utf-8 -*-
"""
语义/条件召回共用：关系类型预筛选（基于 query 的 rerank）
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from data_retrieval.logs.logger import logger
from data_retrieval.tools.graph_tools.driven.external.rerank_client import RerankClient


async def filter_relation_types_by_query(
    relation_types: List[Dict[str, Any]],
    query: Optional[str],
    limit: int,
    logger_instance: Any = None,
) -> List[Dict[str, Any]]:
    """
    基于query对关系类型进行预筛选（使用重排序）。
    """
    if not relation_types:
        return []

    log = logger_instance if logger_instance else logger

    if not query or len(relation_types) <= limit:
        return relation_types[:limit] if len(relation_types) > limit else relation_types

    try:
        candidates = []
        candidate_texts = []
        for rel in relation_types:
            rel_name = rel.get("concept_name", "")
            src = rel.get("source_object_type_id", "")
            tgt = rel.get("target_object_type_id", "")
            text = f"{rel_name} ({src}->{tgt})"
            candidates.append({"text": text, "meta": rel})
            candidate_texts.append(text)

        logger.info(f"[向量重排序] filter_relation_types_by_query：使用向量重排序进行关系类型筛选，关系类型数量={len(candidate_texts)}")
        rerank_client = RerankClient()
        logger.debug(f"[向量重排序] 调用RerankClient.ado_rerank进行关系类型筛选")
        rerank_scores = await rerank_client.ado_rerank(candidate_texts, query or "")
        logger.debug(f"[向量重排序] RerankClient.ado_rerank返回，分数数量={len(rerank_scores) if rerank_scores else 0}")

        if rerank_scores and len(rerank_scores) > 0:
            sorted_scores = sorted(rerank_scores, key=lambda x: x.get("index", 0))
            scored_items = [
                (i, float(item.get("relevance_score", 0.0)))
                for i, item in enumerate(sorted_scores)
                if i < len(candidates)
            ]
            scored_items.sort(key=lambda x: x[1], reverse=True)

            top_k = min(limit, len(scored_items))
            top_indices = [idx for idx, _ in scored_items[:top_k]]

            filtered_relations = []
            for idx in top_indices:
                if 0 <= idx < len(candidates):
                    meta = candidates[idx].get("meta", {})
                    if meta:
                        filtered_relations.append(meta)

            log.info(f"关系类型预筛选完成，保留关系类型 {len(filtered_relations)}/{len(candidates)}，limit={limit}")
            return filtered_relations

        max_k = min(limit, len(relation_types))
        log.warning("关系类型预筛选返回空结果，使用前N个关系类型")
        return relation_types[:max_k]
    except Exception as e:
        max_k = min(limit, len(relation_types))
        log.warning(f"关系类型预筛选失败，改用前{max_k}个关系类型限流。原因: {e}")
        return relation_types[:max_k]


