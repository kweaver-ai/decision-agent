# -*- coding: utf-8 -*-
"""
retrieval_tool 内部使用的纯工具函数集合

从超长的 `retrieval_tool.py` 抽离，降低编排文件复杂度与长度。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from data_retrieval.logs.logger import logger


def filter_properties_mapped_field(properties: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    过滤属性列表中的 mapped_field 字段，避免返回体积过大/字段冗余。
    """
    if not properties or not isinstance(properties, list):
        return properties if isinstance(properties, list) else []

    filtered_properties: List[Dict[str, Any]] = []
    for prop in properties:
        if isinstance(prop, dict):
            filtered_properties.append({k: v for k, v in prop.items() if k != "mapped_field"})
        else:
            filtered_properties.append(prop)

    return filtered_properties


def build_instance_dedup_key(
    instance: Dict[str, Any],
    primary_keys: Optional[List[str]],
    display_key: Optional[str],
) -> str:
    """
    为实例生成去重key：
    1) 优先使用多主键组合；2) 再用显示字段；3) 退化为第一个字段值；4) 最后用id(instance)兜底。
    """
    if not isinstance(instance, dict):
        return str(id(instance))

    if primary_keys:
        pk_parts = []
        for pk in primary_keys:
            if pk in instance:
                pk_parts.append(f"{pk}={instance.get(pk)}")
        if pk_parts:
            return "|".join(pk_parts)

    if display_key and display_key in instance:
        return f"display={instance.get(display_key)}"

    if instance:
        first_key = next(iter(instance.keys()))
        return f"{first_key}={instance.get(first_key)}"

    return str(id(instance))


def merge_semantic_instances_maps(
    keyword_results: List[Tuple[str, Dict[str, List[Dict[str, Any]]]]],
    schema_info: Optional[Dict[str, Any]],
) -> Dict[str, List[Dict[str, Any]]]:
    """
    将多关键词的语义实例结果合并去重。
    去重依据：对象类型下的多主键 / display_key / 首字段值。
    分数策略：优先保留分数高的实例，同时合并 keyword_sources。
    """
    if not keyword_results:
        return {}

    obj_schema_map: Dict[str, Dict[str, Any]] = {}
    if schema_info:
        for obj in schema_info.get("object_types", []):
            cid = obj.get("concept_id")
            if cid:
                obj_schema_map[cid] = {"primary_keys": obj.get("primary_keys") or [], "display_key": obj.get("display_key")}

    merged: Dict[str, Dict[str, Dict[str, Any]]] = {}

    def _get_score(inst: Dict[str, Any]) -> float:
        # 分数来源优先级：
        # - final_score：增强过滤/多信号融合后的最终分
        # - score/rerank_score/direct_score：历史/兼容字段
        # - relevance_score：rerank_utils.rerank_instances 产出的分（不开邻居路径常见）
        for k in ("final_score", "score", "rerank_score", "direct_score", "relevance_score"):
            v = inst.get(k)
            if isinstance(v, (int, float)) and not np.isnan(v):
                return float(v)
        return -1e9

    def _score_fields(inst: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "final_score": inst.get("final_score"),
            "score": inst.get("score"),
            "rerank_score": inst.get("rerank_score"),
            "direct_score": inst.get("direct_score"),
            "relevance_score": inst.get("relevance_score"),
        }

    for keyword, inst_map in keyword_results:
        if not inst_map:
            continue

        for obj_id, inst_list in inst_map.items():
            merged.setdefault(obj_id, {})

            schema = obj_schema_map.get(obj_id, {})
            primary_keys = schema.get("primary_keys", [])
            display_key = schema.get("display_key")

            for inst in inst_list or []:
                key = build_instance_dedup_key(inst, primary_keys, display_key)
                existing = merged[obj_id].get(key)

                inst_copy = inst.copy()
                cur_score = _get_score(inst_copy)
                if cur_score <= -1e8:
                    logger.debug(
                        f"语义实例合并分数缺失，object_type={obj_id}, key={key}, keyword={keyword}, scores={_score_fields(inst_copy)}"
                    )

                kw_sources = set(inst_copy.get("keyword_sources", []))
                kw_sources.add(keyword)
                inst_copy["keyword_sources"] = list(kw_sources)

                if not existing:
                    merged[obj_id][key] = inst_copy
                    continue

                if _get_score(inst_copy) > _get_score(existing):
                    existing_sources = set(existing.get("keyword_sources", []))
                    inst_copy["keyword_sources"] = list(kw_sources.union(existing_sources))
                    merged[obj_id][key] = inst_copy
                else:
                    existing_sources = set(existing.get("keyword_sources", []))
                    existing["keyword_sources"] = list(existing_sources.union(kw_sources))

    return {obj_id: list(dedup_map.values()) for obj_id, dedup_map in merged.items()}


