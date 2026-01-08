# -*- coding: utf-8 -*-
"""
语义实例召回结果的输出规范化/结构转换

从 `retrieval_tool.py` 抽离，减少主文件长度。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ...models import InstancePropertyFilterConfig
from ...infra.utils.instance_utils import InstanceUtils


def filter_semantic_instances_by_global_final_score_ratio(
    semantic_instances_map: Optional[Dict[str, List[Dict[str, Any]]]],
    *,
    ratio: float,
    keep_at_least_one: bool = True,
) -> Optional[Dict[str, List[Dict[str, Any]]]]:
    """
    基于全局 max_final_score 做相对阈值过滤：
      keep if final_score >= max_final_score * ratio

    说明：
    - 仅依赖 `final_score`（若缺失则回退 `relevance_score`，否则视为 0）
    - 不保证每个对象类型都保留实例；过滤后为空的类型会保留空列表
    - keep_at_least_one=True 时，若过滤后全为空，则强制保留全局 top1
    """
    if semantic_instances_map is None:
        return None
    if not isinstance(semantic_instances_map, dict):
        return semantic_instances_map
    if not semantic_instances_map:
        return semantic_instances_map

    try:
        ratio_f = float(ratio)
    except Exception:
        ratio_f = 0.0
    if ratio_f <= 0.0:
        return semantic_instances_map

    def _get_score(inst: Dict[str, Any]) -> float:
        if not isinstance(inst, dict):
            return 0.0
        v = inst.get("final_score")
        if v is None:
            v = inst.get("relevance_score")
        try:
            return float(v) if v is not None else 0.0
        except Exception:
            return 0.0

    # 1) 找全局 max 与 top1
    max_s = 0.0
    top_obj_id = None
    top_inst = None
    top_s = None
    for obj_id, insts in semantic_instances_map.items():
        if not isinstance(insts, list):
            continue
        for inst in insts:
            s = _get_score(inst)
            if top_s is None or s > top_s:
                top_s = s
                top_obj_id = obj_id
                top_inst = inst
            if s > max_s:
                max_s = s

    if max_s <= 0.0:
        # 分数不可用（全0/无分数）时不做过滤，避免误伤
        return semantic_instances_map

    threshold = max_s * ratio_f

    # 2) 过滤
    filtered_map: Dict[str, List[Dict[str, Any]]] = {}
    total_kept = 0
    for obj_id, insts in semantic_instances_map.items():
        if not isinstance(insts, list):
            continue
        kept = [inst for inst in insts if _get_score(inst) >= threshold]
        filtered_map[obj_id] = kept
        total_kept += len(kept)

    # 3) 兜底：至少保留全局 top1
    if total_kept == 0 and keep_at_least_one and top_obj_id and isinstance(top_inst, dict):
        filtered_map = {k: [] for k in semantic_instances_map.keys()}
        filtered_map[top_obj_id] = [top_inst]

    # 补齐输入中存在但未遍历到的 key（结构稳定）
    for obj_id in semantic_instances_map.keys():
        filtered_map.setdefault(obj_id, [])

    return filtered_map


def _filter_data_properties(
    data_properties: Dict[str, Any],
    *,
    display_key: Optional[str],
    primary_keys: List[str],
    property_filter_config: Optional[InstancePropertyFilterConfig],
) -> Dict[str, Any]:
    """
    对实例 data_properties 做轻量过滤，避免返回体过大。

    约定：
    - 输出字段名使用 `data_properties`（与概念召回 schema 的字段命名保持一致）
    - 不强依赖语义匹配字段（语义实例召回场景没有 matched_fields）
    """
    if not isinstance(data_properties, dict) or not data_properties:
        return {}

    # 1) 先移除主键字段：主键统一通过 unique_identities 返回，避免重复/歧义
    filtered: Dict[str, Any] = {}
    for k, v in data_properties.items():
        # 注意：display_key 可能也在 primary_keys 里（例如 name 既是展示字段又是主键的一部分），
        # 此时仍应保留展示字段在 data_properties 中，避免“实例数据属性”缺失关键字段。
        if k in (primary_keys or []) and (not display_key or k != display_key):
            continue
        filtered[k] = v

    cfg = property_filter_config or InstancePropertyFilterConfig()
    enable_filter = bool(getattr(cfg, "enable_property_filter", True))
    if not enable_filter:
        return filtered

    try:
        max_props = int(getattr(cfg, "max_properties_per_instance", 20) or 20)
    except Exception:
        max_props = 20
    try:
        max_len = int(getattr(cfg, "max_property_value_length", 500) or 500)
    except Exception:
        max_len = 500

    if max_props <= 0:
        max_props = 20
    if max_len <= 0:
        max_len = 500

    # 2) 价值排序：优先保留 display_key（若存在），其余按原始顺序保留
    keys: List[str] = list(filtered.keys())
    if display_key and display_key in filtered:
        keys = [display_key] + [k for k in keys if k != display_key]

    # 3) 截断数量 + 截断字符串长度
    out: Dict[str, Any] = {}
    for k in keys[:max_props]:
        v = filtered.get(k)
        if isinstance(v, str) and len(v) > max_len:
            out[k] = v[:max_len]
        else:
            out[k] = v
    return out


def normalize_semantic_instances_for_output(
    semantic_instances_map: Optional[Dict[str, List[Dict[str, Any]]]],
    schema_info: Optional[Dict[str, Any]],
    property_filter_config: Optional[InstancePropertyFilterConfig] = None,
) -> Optional[Dict[str, List[Dict[str, Any]]]]:
    """
    统一规范化语义实例输出：
    - 保证返回 unique_identities（至少是空dict）
    - 每条实例保留三类信息：
      1) 展示名字段（来自 schema.display_key 或 fallback 规则）
      2) unique_identities（主键字典）
      3) data_properties（实例数据属性，字段命名与概念召回保持一致；按 property_filter 规则限流）
    """
    if semantic_instances_map is None:
        return None
    if not isinstance(semantic_instances_map, dict):
        return semantic_instances_map

    obj_schema_map: Dict[str, Dict[str, Any]] = {}
    if schema_info and isinstance(schema_info, dict):
        for obj in schema_info.get("object_types", []) or []:
            cid = obj.get("concept_id") or obj.get("id")
            if cid:
                obj_schema_map[cid] = {
                    "primary_keys": obj.get("primary_keys") or [],
                    "display_key": obj.get("display_key"),
                }

    normalized: Dict[str, List[Dict[str, Any]]] = {}
    for obj_id, inst_list in semantic_instances_map.items():
        if not isinstance(inst_list, list):
            normalized[obj_id] = inst_list  # 兼容异常数据
            continue

        schema = obj_schema_map.get(obj_id, {}) or {}
        primary_keys = schema.get("primary_keys", []) or []
        display_key = schema.get("display_key")

        out_list: List[Dict[str, Any]] = []
        for inst in inst_list:
            if not isinstance(inst, dict):
                continue

            inst_copy = inst.copy()

            unique_identities = inst_copy.get("unique_identities", {})
            if not isinstance(unique_identities, dict) or unique_identities is None:
                unique_identities = {}
            if not unique_identities and primary_keys:
                unique_identities = InstanceUtils.extract_unique_identities(inst_copy, primary_keys)
            unique_identities = unique_identities if isinstance(unique_identities, dict) else {}

            out_display_key = display_key
            out_display_val = None
            # 1) 优先使用 display_key；如果字段本身不存在，再从 unique_identities 中兜底
            if display_key:
                if display_key in inst_copy and inst_copy.get(display_key) not in (None, ""):
                    out_display_val = inst_copy.get(display_key)
                elif unique_identities.get(display_key) not in (None, ""):
                    out_display_val = unique_identities.get(display_key)
            # 2) 若仍然没有可用展示值，再按规则从 *_name/name/display 中回退
            if out_display_val is None:
                for k, v in inst_copy.items():
                    if isinstance(k, str) and k.endswith("_name") and v not in (None, ""):
                        out_display_key = k
                        out_display_val = v
                        break
                if out_display_val is None:
                    if "name" in inst_copy and inst_copy.get("name") not in (None, ""):
                        out_display_key = "name"
                        out_display_val = inst_copy.get("name")
                    elif "display" in inst_copy and inst_copy.get("display") not in (None, ""):
                        out_display_key = "display"
                        out_display_val = inst_copy.get("display")
                    else:
                        out_display_key = out_display_key or "display"
                        out_display_val = ""

            # 保留分数信息：用于跨对象类型全局排序与调试日志
            # - 优先使用上游挂载的 final_score
            # - 若缺失，则尝试回退到 rerank 产生的 relevance_score
            score_val = None
            if inst_copy.get("final_score") is not None:
                score_val = inst_copy.get("final_score")
            elif inst_copy.get("relevance_score") is not None:
                score_val = inst_copy.get("relevance_score")

            # data_properties：尽量保留实例字段（不把它们打散到顶层，避免与展示字段/unique_identities 混杂）
            # - 兼容：如果上游提供了 properties 字段（dict），优先用它
            # - 否则：把除内部元字段外的顶层字段作为 data_properties
            raw_props: Dict[str, Any] = {}
            if isinstance(inst_copy.get("properties"), dict):
                raw_props = inst_copy.get("properties") or {}
            else:
                # 排除内部字段
                exclude_keys = {
                    "unique_identities",
                    "final_score",
                    "relevance_score",
                    "keyword_sources",
                    "_is_direct_match",
                }
                raw_props = {k: v for k, v in inst_copy.items() if k not in exclude_keys}

            data_properties = _filter_data_properties(
                raw_props,
                display_key=display_key,
                primary_keys=primary_keys,
                property_filter_config=property_filter_config,
            )

            out_item = {
                out_display_key: out_display_val,
                "unique_identities": unique_identities,
                "data_properties": data_properties,
            }
            if score_val is not None:
                try:
                    out_item["final_score"] = float(score_val)
                except Exception:
                    pass

            out_list.append(out_item)

        normalized[obj_id] = out_list

    return normalized


def semantic_instances_map_to_nodes(
    semantic_instances_map: Optional[Dict[str, List[Dict[str, Any]]]]
) -> List[Dict[str, Any]]:
    """
    将语义实例召回的 map 结构扁平化为条件召回同款 nodes 结构：
    - 输入：{object_type_id: [ {<display_key>: <name>, unique_identities: {...}}, ... ]}
    - 输出：[ {object_type_id: "...", "<object_type_id>_name": "...", unique_identities: {...}}, ... ]
    """
    if not semantic_instances_map or not isinstance(semantic_instances_map, dict):
        return []

    # -----------------------------
    # 1. 扁平化 + 计算每条实例的基础分/类型内归一化分
    # -----------------------------
    flat_items: List[Dict[str, Any]] = []
    type_to_scores: Dict[str, List[float]] = {}

    for object_type_id, inst_list in semantic_instances_map.items():
        if not isinstance(inst_list, list):
            continue

        obj_id = (str(object_type_id) if object_type_id is not None else "").strip()
        for inst in inst_list:
            if not isinstance(inst, dict):
                continue
            item = inst.copy()
            item["object_type_id"] = obj_id
            # 基础分：来自上游挂载的 final_score；若没有则为 0.0
            base_score = 0.0
            try:
                if "final_score" in item and item["final_score"] is not None:
                    base_score = float(item["final_score"])
            except Exception:
                base_score = 0.0
            item["_base_score"] = base_score
            flat_items.append(item)
            type_to_scores.setdefault(obj_id, []).append(base_score)

    if not flat_items:
        return []

    # 计算每个类型内的均值/标准差，用于相对归一化
    type_norm_stats: Dict[str, Dict[str, float]] = {}
    for obj_id, scores in type_to_scores.items():
        if not scores:
            type_norm_stats[obj_id] = {"mean": 0.0, "std": 0.0, "min": 0.0, "max": 0.0}
            continue
        n = float(len(scores))
        mean = sum(scores) / n
        var = sum((s - mean) ** 2 for s in scores) / n
        std = var ** 0.5
        min_s = min(scores)
        max_s = max(scores)
        type_norm_stats[obj_id] = {"mean": mean, "std": std, "min": min_s, "max": max_s}

    # -----------------------------
    # 2. 组合分数：绝对分 + 类型内相对分
    # -----------------------------
    alpha = 0.7  # 绝对分权重
    # 默认使用 min-max 归一化（0~1），避免 Z-score 在 std 很小/分布很窄时数值爆炸，
    # 导致“绝对分明显更高”的实例反而被挤到后面。
    use_z_score = False
    eps = 1e-6

    for item in flat_items:
        obj_id = item.get("object_type_id") or ""
        base_score = float(item.get("_base_score", 0.0) or 0.0)
        stats = type_norm_stats.get(obj_id, {"mean": 0.0, "std": 0.0, "min": 0.0, "max": 0.0})
        rel_score = 0.0
        if use_z_score:
            std = stats.get("std", 0.0)
            mean = stats.get("mean", 0.0)
            if std > eps:
                rel_score = (base_score - mean) / std
        else:
            s_min = stats.get("min", 0.0)
            s_max = stats.get("max", 0.0)
            if s_max - s_min > eps:
                rel_score = (base_score - s_min) / (s_max - s_min)
        # 归一化分做一个安全截断，避免极端值影响全局排序
        if rel_score > 1.0:
            rel_score = 1.0
        elif rel_score < 0.0:
            rel_score = 0.0

        final_score = alpha * base_score + (1.0 - alpha) * rel_score
        item["_combined_score"] = final_score

    # -----------------------------
    # 3. 全局排序（按 combined_score 降序）
    # -----------------------------
    flat_items.sort(key=lambda x: x.get("_combined_score", 0.0), reverse=True)

    # -----------------------------
    # 4. 按原有规范生成 nodes 结构
    # -----------------------------
    nodes: List[Dict[str, Any]] = []
    for item in flat_items:
        obj_id = (item.get("object_type_id") or "").strip()
        name_key = f"{obj_id}_name" if obj_id else "name"

        display_val = None
        if name_key in item and item.get(name_key) not in (None, ""):
            display_val = item.get(name_key)
        else:
            for k, v in item.items():
                if isinstance(k, str) and k.endswith("_name") and v not in (None, ""):
                    display_val = v
                    break
            if display_val is None:
                display_val = item.get("name") or item.get("display") or ""

        unique_identities = item.get("unique_identities") or {}
        if not isinstance(unique_identities, dict):
            unique_identities = {}

        node: Dict[str, Any] = {
            "object_type_id": obj_id,
            name_key: display_val,
            "unique_identities": unique_identities,
        }
        # 显式透出 final_score（用于调试/阈值/前端展示）
        if item.get("final_score") is not None:
            try:
                node["final_score"] = float(item.get("final_score") or 0.0)
            except Exception:
                pass
        data_properties = item.get("data_properties")
        if isinstance(data_properties, dict):
            # 字段命名保持与概念召回一致：data_properties
            node["data_properties"] = data_properties
        nodes.append(node)

    return nodes


