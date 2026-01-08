# -*- coding: utf-8 -*-
"""
最终检索结果构建（object_types / relation_types）

从 `retrieval_tool.py` 抽离，降低主编排文件复杂度。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from data_retrieval.logs.logger import logger

from ...services.session.session_manager import RetrievalSessionManager
from .tool_utils import filter_properties_mapped_field
from .session_persist import persist_and_build_return


async def build_final_result(
    *,
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
    """
    构建最终检索结果。

    注意：此函数是从原 `_build_final_result` 迁移而来，尽量保持行为一致。
    """
    object_types: List[Dict[str, Any]] = []
    relation_types: List[Dict[str, Any]] = []

    # 获取知识网络ID（保持与原逻辑一致，覆盖传入 kn_id）
    kn_id = network_details.get("id")

    filtered_objects_mapping, relevant_relations = relevant_concepts

    for rel in relevant_relations:
        if "source" in rel and "target" in rel:
            source_obj_id = rel.get("source", {}).get("id")
            target_obj_id = rel.get("target", {}).get("id")
        else:
            source_obj_id = rel.get("source_object_type_id")
            target_obj_id = rel.get("target_object_type_id")

        relation_types.append(
            {
                "concept_type": "relation_type",
                "concept_id": rel["id"],
                "concept_name": rel["name"],
                "comment": rel.get("comment") or None,
                "source_object_type_id": source_obj_id,
                "target_object_type_id": target_obj_id,
                "kn_id": kn_id,
            }
        )

    object_type_primary_keys: Dict[str, List[str]] = {}
    object_type_display_keys: Dict[str, str] = {}
    if network_details and isinstance(network_details, dict):
        object_types_list = network_details.get("object_types", [])

        if object_types_list:
            try:
                summary = []
                for obj_type in object_types_list:
                    if isinstance(obj_type, dict):
                        summary.append(
                            {
                                "id": obj_type.get("id"),
                                "primary_keys": obj_type.get("primary_keys"),
                                "primary_key_field": obj_type.get("primary_key_field"),
                                "display_key": obj_type.get("display_key"),
                            }
                        )
                logger.debug(f"network_details主键信息: {summary}")
            except Exception as log_e:
                logger.warning(f"记录network_details主键信息失败: {log_e}")

            for obj_type in object_types_list:
                if not isinstance(obj_type, dict):
                    continue
                obj_type_id = obj_type.get("id")
                primary_keys = obj_type.get("primary_keys", [])
                if not primary_keys or (isinstance(primary_keys, list) and len(primary_keys) == 0):
                    primary_key_field = obj_type.get("primary_key_field")
                    if primary_key_field:
                        primary_keys = [primary_key_field]
                display_key = obj_type.get("display_key")

                if obj_type_id:
                    if primary_keys and isinstance(primary_keys, list) and len(primary_keys) > 0:
                        object_type_primary_keys[obj_type_id] = primary_keys
                    else:
                        logger.warning(
                            f"对象类型 {obj_type_id} 未找到主键字段。"
                            f"API返回的keys: {list(obj_type.keys())}, "
                            f"primary_keys值: {obj_type.get('primary_keys')}, "
                            f"primary_key_field值: {obj_type.get('primary_key_field')}"
                        )

        if obj_type_id and display_key:
            object_type_display_keys[obj_type_id] = display_key

    # 摘要日志：主键和显示键统计
    logger.debug(
        f"主键映射完成：{len(object_type_primary_keys)} 个对象类型有主键信息，"
        f"显示键映射完成：{len(object_type_display_keys)} 个对象类型有显示键"
    )

    # 为避免在 network_details 获取失败时出现 UnboundLocalError，这里为 object_types_list 提供安全默认值
    object_types_list: List[Dict[str, Any]] = []

    # 仅在后续成功从 network_details 解析到 object_types_list 时，才输出下面的告警日志
    try:
        if network_details and isinstance(network_details, dict):
            object_types_list = network_details.get("object_types", []) or []

        if not object_type_primary_keys and object_types_list:
            logger.warning(
                f"从network_details中找到 {len(object_types_list)} 个对象类型，但未找到任何主键信息。"
                f"第一个对象类型的keys: {list(object_types_list[0].keys()) if object_types_list else 'empty'}"
            )
        elif not object_types_list:
            logger.warning(
                f"network_details中未找到object_types字段，network_details的keys: {list(network_details.keys()) if isinstance(network_details, dict) else 'not-dict'}"
            )
    except Exception as e:
        # 日志统计本身不应影响主流程，异常时仅记录调试信息
        logger.debug(f"统计object_types_list信息时出错: {e}", exc_info=True)

    sample_data_map: Dict[str, Optional[Dict[str, Any]]] = {}
    if include_sample_data and session_id and kn_id:
        sample_data_map = RetrievalSessionManager.get_all_sample_data(session_id, kn_id)
        logger.info(f"从session获取样例数据，共 {len(sample_data_map)} 个对象类型")
        if sample_data_map:
            logger.debug(f"样例数据对象类型ID列表: {list(sample_data_map.keys())}")
        else:
            logger.warning(f"Session中没有样例数据，session_id={session_id}, kn_id={kn_id}")

    obj_detail_map: Dict[str, Dict[str, Any]] = {}
    try:
        if network_details and isinstance(network_details, dict):
            object_types = network_details.get("object_types", []) or []
            logger.debug(f"从network_details中获取到 {len(object_types)} 个对象类型用于构建obj_detail_map")
            for _d in object_types:
                if isinstance(_d, dict) and _d.get("id"):
                    obj_id = _d["id"]
                    obj_detail_map[obj_id] = _d
    except Exception as e:
        logger.warning(f"构建obj_detail_map失败: {e}", exc_info=True)

    # 统计对象类型处理情况，用于摘要日志
    total_obj_types = len(filtered_objects_mapping or {})
    obj_types_with_detail = 0
    obj_types_with_data_props_from_network = 0
    obj_types_with_data_props_from_mapping = 0
    obj_types_missing_props = 0

    # 属性分数获取（概念召回阶段已写入）；仅在启用属性裁剪时尝试读取
    property_scores: Dict[str, float] = {}
    if enable_property_brief:
        # 优先从 session 中获取属性分数（如果有 session_id）
        if session_id and kn_id:
            try:
                property_scores = RetrievalSessionManager.get_all_property_scores(session_id, kn_id) or {}
            except Exception as e:
                logger.warning(
                    "从session获取属性分数失败，将尝试从临时session获取: %s", str(e), exc_info=True
                )
        
        # 如果从 session 中获取失败或没有 session_id，尝试从临时 session 中获取
        # 临时 session_id 用于存储没有 session_id 时的属性分数
        if not property_scores and kn_id:
            try:
                temp_session_id = f"_temp_property_scores_{kn_id}"
                property_scores = RetrievalSessionManager.get_all_property_scores(temp_session_id, kn_id) or {}
                if property_scores:
                    logger.debug(
                        "从临时session获取到属性分数（temp_session_id=%s, kn_id=%s），共 %d 个属性分数",
                        temp_session_id, kn_id, len(property_scores)
                    )
            except Exception as e:
                logger.debug(
                    "从临时session获取属性分数失败: %s", str(e)
                )
        
        # 如果 property_scores 仍然为空，说明没有可用的属性分数，将降级为不对属性做裁剪
        if not property_scores:
            logger.debug(
                "未找到属性分数（session_id=%s, kn_id=%s），将不对最终schema属性做裁剪",
                session_id, kn_id
            )
            enable_property_brief = False

    # 第一轮遍历：收集对象信息和属性源，便于后续统一做“必留 + 相关性裁剪”
    collected_objs = []
    for _, obj in (filtered_objects_mapping or {}).items():
        obj_id = obj.get("id")
        obj_name = obj.get("name")
        if not obj_id:
            continue

        obj_type_from_network = obj_detail_map.get(obj_id) if obj_id else None
        if obj_type_from_network:
            obj_types_with_detail += 1

        properties = None
        if isinstance(obj_type_from_network, dict):
            properties = obj_type_from_network.get("data_properties")
            if properties is None or not isinstance(properties, list):
                old_props = obj_type_from_network.get("properties")
                if old_props is not None and isinstance(old_props, list):
                    properties = old_props
                    obj_types_with_data_props_from_network += 1
                else:
                    properties = None
                    obj_types_missing_props += 1
            elif len(properties) > 0:
                obj_types_with_data_props_from_network += 1

        if properties is None or (isinstance(properties, list) and len(properties) == 0):
            obj_props = obj.get("data_properties")
            if obj_props is not None and isinstance(obj_props, list) and len(obj_props) > 0:
                properties = obj_props
                obj_types_with_data_props_from_mapping += 1
            elif properties is None:
                properties = []

        if properties is None:
            properties = []

        logic_properties = []
        if isinstance(obj_type_from_network, dict):
            logic_properties = obj_type_from_network.get("logic_properties")
            if not (logic_properties and isinstance(logic_properties, list)):
                logic_properties = []
        if not logic_properties:
            logic_properties = obj.get("logic_properties")
            if logic_properties is None or not isinstance(logic_properties, list):
                logic_properties = []

        comment = (obj.get("comment") or "").strip()
        if (not comment) and isinstance(obj_type_from_network, dict):
            comment = (obj_type_from_network.get("comment") or "").strip()

        primary_keys = object_type_primary_keys.get(obj_id)
        display_key = object_type_display_keys.get(obj_id)

        filtered_properties = filter_properties_mapped_field(properties)

        collected_objs.append(
            {
                "obj": obj,
                "obj_id": obj_id,
                "obj_name": obj_name,
                "comment": comment,
                "primary_keys": primary_keys,
                "display_key": display_key,
                "data_properties": filtered_properties,
                "logic_properties": logic_properties,
            }
        )

    # 计算属性裁剪：仅在 schema_brief & enable_property_brief & 有分数时生效
    selected_properties_by_obj: Dict[str, List[Dict[str, Any]]] = {}
    if enable_property_brief and property_scores and collected_objs:
        # 先按对象做预筛，再做全局截断，必留字段无条件保留
        global_candidates: List[Tuple[float, str, str, Dict[str, Any]]] = []
        mandatory_props_by_obj: Dict[str, List[Dict[str, Any]]] = {}
        candidate_props_by_obj: Dict[str, List[Tuple[float, Dict[str, Any], str]]] = {}

        for rec in collected_objs:
            obj_id = rec["obj_id"]
            props = rec["data_properties"] or []
            pk_list = rec.get("primary_keys") or []
            display_key = rec.get("display_key")
            mandatory_names = set(pk_list or [])
            if display_key:
                mandatory_names.add(display_key)

            mandatory_list: List[Dict[str, Any]] = []
            scored_list: List[Tuple[float, Dict[str, Any], str]] = []

            for prop in props:
                if not isinstance(prop, dict):
                    continue
                key = (prop.get("display_name") or prop.get("name") or "").strip()
                if not key:
                    continue
                if key in mandatory_names:
                    mandatory_list.append(prop)
                    continue
                score = property_scores.get(f"{obj_id}_{key}")
                if isinstance(score, (int, float)):
                    scored_list.append((float(score), prop, key))

            # 每对象预筛
            scored_list.sort(key=lambda x: x[0], reverse=True)
            top_n = max(int(per_object_property_top_k or 1), 1)
            top_scored = scored_list[:top_n]

            mandatory_props_by_obj[obj_id] = mandatory_list
            candidate_props_by_obj[obj_id] = top_scored

            for sc, prop, key in top_scored:
                global_candidates.append((sc, obj_id, key, prop))

        # 全局截断（非必留）
        global_candidates.sort(key=lambda x: x[0], reverse=True)
        g_top = max(int(global_property_top_k or 1), 1)
        allowed_non_mand_keys = set()
        for sc, obj_id, key, _ in global_candidates[:g_top]:
            allowed_non_mand_keys.add((obj_id, key))

        # 汇总最终保留属性（必留 + 全局入选）
        for rec in collected_objs:
            obj_id = rec["obj_id"]
            props = rec["data_properties"] or []
            pk_list = rec.get("primary_keys") or []
            display_key = rec.get("display_key")
            mandatory_names = set(pk_list or [])
            if display_key:
                mandatory_names.add(display_key)

            final_props: List[Dict[str, Any]] = []
            for prop in props:
                if not isinstance(prop, dict):
                    continue
                key = (prop.get("display_name") or prop.get("name") or "").strip()
                if not key:
                    continue
                if key in mandatory_names:
                    final_props.append(prop)
                    continue
                if (obj_id, key) in allowed_non_mand_keys:
                    final_props.append(prop)
            selected_properties_by_obj[obj_id] = final_props

    # 第二轮遍历：构建最终返回的 object_types
    for rec in collected_objs:
        obj = rec["obj"]
        obj_id = rec["obj_id"]
        filtered_properties = rec["data_properties"]
        logic_properties = rec["logic_properties"]
        primary_keys = rec["primary_keys"]
        display_key = rec["display_key"]
        comment = rec["comment"]

        # 如果开启属性裁剪且有结果，则替换 data_properties
        if enable_property_brief and selected_properties_by_obj.get(obj_id):
            filtered_properties = selected_properties_by_obj[obj_id]

        if not primary_keys:
            logger.warning(
                f"对象类型 {obj_id} 未找到主键字段（primary_keys或primary_key_field），"
                f"这可能导致后续条件检索失败。请检查API返回的schema信息。"
                f"已收集的主键映射keys: {list(object_type_primary_keys.keys())}"
            )

        object_type_info: Dict[str, Any] = {
            "concept_type": "object_type",
            "concept_id": obj_id,
            "concept_name": rec["obj_name"],
            "comment": (comment or None),
            "kn_id": kn_id,
            "data_properties": filtered_properties,
            "logic_properties": logic_properties,
            "primary_keys": primary_keys if primary_keys else [],
            "display_key": display_key,
        }

        if include_sample_data:
            sample_data = sample_data_map.get(obj_id)
            object_type_info["sample_data"] = sample_data

        # NOTE: 语义实例统一通过 nodes 返回，不再绑定到对象类型（避免返回体膨胀与重复字段）。

        object_types.append(object_type_info)

    # 摘要日志：对象类型处理统计
    logger.info(
        f"对象类型处理完成：总计 {total_obj_types} 个，"
        f"有完整detail的 {obj_types_with_detail} 个，"
        f"从network获取data_properties的 {obj_types_with_data_props_from_network} 个，"
        f"从mapping获取data_properties的 {obj_types_with_data_props_from_mapping} 个，"
        f"缺少data_properties的 {obj_types_missing_props} 个"
    )

    # 从network_details中提取action_types
    action_types: List[Dict[str, Any]] = []
    if network_details and isinstance(network_details, dict):
        action_types = network_details.get("action_types", [])
        if action_types and isinstance(action_types, list):
            logger.debug(f"从network_details中提取到 {len(action_types)} 个action_types")
        else:
            logger.debug(f"network_details中未找到action_types字段或格式不正确")

    result = {"object_types": object_types, "relation_types": relation_types, "action_types": action_types}

    logger.debug(f"最终检索结果构建完成，对象类型: {len(object_types)} 项，关系类型: {len(relation_types)} 项，操作类型: {len(action_types)} 项")

    if session_id and result and kn_id:
        return persist_and_build_return(
            session_id=session_id,
            current_kn_id=kn_id,
            result=result,
            network_details=network_details,
            return_union=return_union,
            include_sample_data=include_sample_data,
            filter_properties=filter_properties_mapped_field,
        )

    return result


