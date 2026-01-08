# -*- coding: utf-8 -*-
"""
将检索结果写入 session，并根据 return_union 返回并集或增量结果

从 `retrieval_tool.py` 抽离，降低主编排文件复杂度。
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Tuple

from data_retrieval.logs.logger import logger

from ...services.session.session_manager import RetrievalSessionManager


FilterPropsFn = Callable[[List[Dict[str, Any]]], List[Dict[str, Any]]]


def persist_and_build_return(
    *,
    session_id: str,
    current_kn_id: str,
    result: Dict[str, List[Dict[str, Any]]],
    network_details: Dict[str, Any],
    return_union: bool,
    include_sample_data: bool,
    filter_properties: FilterPropsFn,
) -> Dict[str, List[Dict[str, Any]]]:
    """
    - 将 result 写入 session（按 kn_id 分组）
    - return_union=True：返回所有轮次并集（并补齐 sample_data）
    - return_union=False：返回当前轮次增量（相对之前轮次的并集）
    """
    if not session_id or not result:
        return result

    all_results = (result.get("object_types") or []) + (result.get("relation_types") or [])

    results_by_kn: Dict[str, List[Dict[str, Any]]] = {}

    for res in all_results:
        result_kn_id = res.get("kn_id", "unknown")
        results_by_kn.setdefault(result_kn_id, [])

        enhanced_result = res.copy()

        kn_detail = None
        if network_details and network_details.get("id") == result_kn_id:
            kn_detail = network_details

        if kn_detail:
            enhanced_result["kn_name"] = kn_detail.get("name", "")
            enhanced_result["kn_comment"] = kn_detail.get("comment", "")

        results_by_kn[result_kn_id].append(enhanced_result)

    for save_kn_id, enhanced_results in results_by_kn.items():
        RetrievalSessionManager.add_retrieval_record(session_id, save_kn_id, enhanced_results)
        logger.info(f"已将 {len(enhanced_results)} 条检索结果保存到会话 {session_id} 的知识网络 {save_kn_id} 中")

    if return_union:
        all_rounds_union = RetrievalSessionManager.get_all_rounds_union(session_id, current_kn_id)
        union_object_count = sum(1 for item in all_rounds_union if item.get("concept_type") == "object_type")
        union_relation_count = sum(1 for item in all_rounds_union if item.get("concept_type") == "relation_type")
        logger.info(
            f"获取知识网络 {current_kn_id} 的所有轮次并集（已包含当前结果），"
            f"对象类型: {union_object_count} 项，关系类型: {union_relation_count} 项，总计: {len(all_rounds_union)} 项"
        )

        union_sample_data_map: Dict[str, Optional[Dict[str, Any]]] = {}
        if include_sample_data and session_id and current_kn_id:
            union_sample_data_map = RetrievalSessionManager.get_all_sample_data(session_id, current_kn_id)
            logger.debug(f"从session获取并集样例数据，共 {len(union_sample_data_map)} 个对象类型")

        union_object_types: List[Dict[str, Any]] = []
        union_relation_types: List[Dict[str, Any]] = []

        for item in all_rounds_union:
            if item.get("concept_type") == "object_type":
                item_copy = item.copy()

                if "data_properties" in item_copy and isinstance(item_copy["data_properties"], list):
                    item_copy["data_properties"] = filter_properties(item_copy["data_properties"])

                if include_sample_data and "sample_data" not in item_copy:
                    object_type_id = item_copy.get("concept_id")
                    if object_type_id:
                        item_copy["sample_data"] = union_sample_data_map.get(object_type_id)

                union_object_types.append(item_copy)
            elif item.get("concept_type") == "relation_type":
                union_relation_types.append(item)

        # 从network_details中提取action_types（仅在第一轮或return_union=True时返回）
        action_types: List[Dict[str, Any]] = []
        if network_details and isinstance(network_details, dict):
            action_types = network_details.get("action_types", [])
        
        final_result = {"object_types": union_object_types, "relation_types": union_relation_types, "action_types": action_types}
    else:
        # 增量：当前结果 - 之前轮次并集
        current_records = RetrievalSessionManager._session_records[session_id][current_kn_id]["retrieval_results"]
        all_rounds = RetrievalSessionManager._get_rounds_for_kn(current_records)
        current_round = max(all_rounds) if all_rounds else 1

        previous_rounds_union = RetrievalSessionManager.get_previous_rounds_union(
            session_id, current_kn_id, exclude_current_round=current_round
        )

        previous_keys = set()
        for item in previous_rounds_union:
            concept_id = item.get("concept_id", "")
            concept_type = item.get("concept_type", "")
            previous_keys.add((concept_id, concept_type))

        current_results = (result.get("object_types") or []) + (result.get("relation_types") or [])
        incremental_object_types: List[Dict[str, Any]] = []
        incremental_relation_types: List[Dict[str, Any]] = []

        for item in current_results:
            concept_id = item.get("concept_id", "")
            concept_type = item.get("concept_type", "")
            unique_key = (concept_id, concept_type)

            if concept_type == "object_type":
                schema_is_new = unique_key not in previous_keys
                if not schema_is_new:
                    continue

                # 增量返回策略：
                # - schema_is_new=True：返回 schema（字段/主键/展示字段等），供下游理解与后续条件检索
                # - 语义实例增量由 nodes 的 session 逻辑单独处理（不绑定在 object_types 下）
                incremental_obj_type: Dict[str, Any] = {
                    "concept_type": item.get("concept_type", ""),
                    "concept_id": item.get("concept_id", ""),
                    "concept_name": item.get("concept_name", ""),
                }

                if schema_is_new:
                    properties = item.get("data_properties", [])
                    filtered_properties = filter_properties(properties if isinstance(properties, list) else [])
                    incremental_obj_type["data_properties"] = filtered_properties

                    if "comment" in item:
                        incremental_obj_type["comment"] = item.get("comment")
                    if "logic_properties" in item:
                        incremental_obj_type["logic_properties"] = item.get("logic_properties", [])

                    if "primary_keys" in item:
                        incremental_obj_type["primary_keys"] = item.get("primary_keys", [])
                    elif "primary_key_field" in item:
                        # 兼容旧字段名
                        pkf = item.get("primary_key_field")
                        if pkf:
                            incremental_obj_type["primary_keys"] = [pkf]

                    if "display_key" in item:
                        incremental_obj_type["display_key"] = item.get("display_key")
                    if "sample_data" in item:
                        incremental_obj_type["sample_data"] = item.get("sample_data")

                incremental_object_types.append(incremental_obj_type)

            elif concept_type == "relation_type":
                if unique_key in previous_keys:
                    continue
                incremental_relation_types.append(
                    {
                        "concept_type": item.get("concept_type", ""),
                        "concept_id": item.get("concept_id", ""),
                        "concept_name": item.get("concept_name", ""),
                        "source_object_type_id": item.get("source_object_type_id"),
                        "target_object_type_id": item.get("target_object_type_id"),
                    }
                )

        # action_types 通常是知识网络级别的“静态信息”，每轮重复返回会造成不必要的体积与带宽开销。
        # 最佳实践：增量模式仅在第一轮返回 action_types；后续轮次返回空数组（客户端可在首轮缓存）。
        action_types: List[Dict[str, Any]] = []
        if current_round == 1 and network_details and isinstance(network_details, dict):
            action_types = network_details.get("action_types", []) or []
        
        final_result = {"object_types": incremental_object_types, "relation_types": incremental_relation_types, "action_types": action_types}
        logger.info(
            f"获取知识网络 {current_kn_id} 第{current_round}轮的增量结果，"
            f"新增对象类型: {len(incremental_object_types)} 项，新增关系类型: {len(incremental_relation_types)} 项"
        )

    session_info = RetrievalSessionManager.get_session_info()
    logger.debug(f"当前活跃会话数: {session_info['active_sessions']}, 总记录数: {session_info['total_records']}")

    return final_result


