# -*- coding: utf-8 -*-
"""
schema_info 构建/补齐逻辑

从 `retrieval_tool.py` 抽离，避免主编排文件过长。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from data_retrieval.logs.logger import logger

from ...services.session.session_manager import RetrievalSessionManager


def get_schema_info(
    session_id: Optional[str],
    kn_id: str,
    network_details: Optional[Dict[str, Any]] = None,
    filtered_objects: Optional[Dict[str, Any]] = None,
    filtered_relations: Optional[List[Dict[str, Any]]] = None,
    raise_on_error: bool = False,
) -> Optional[Dict[str, Any]]:
    """
    获取 schema 信息（对象类型和关系类型）。

    - 优先从 session 获取合并后的 schema_info（包含所有轮次的关系类型）
    - 如果无法获取，则使用当前轮次的数据构建新的 schema_info
    - 如果从 session 获取成功，则会补齐当前轮次召回的对象类型（基于 network_details 的完整字段）
    """
    schema_info = None
    if session_id:
        schema_info = RetrievalSessionManager.get_schema_info(session_id, kn_id)
        if schema_info:
            logger.debug(
                f"从session获取合并后的schema_info，"
                f"对象类型: {len(schema_info.get('object_types', []))} 项，"
                f"关系类型: {len(schema_info.get('relation_types', []))} 项"
            )

    if not schema_info:
        if not network_details or not filtered_objects:
            if raise_on_error:
                raise ValueError("无法获取schema_info：既无法从session获取，也没有提供network_details和filtered_objects")
            logger.warning("无法获取schema_info：既无法从session获取，也没有提供network_details和filtered_objects")
            return None

        schema_object_types = []
        if isinstance(network_details, dict):
            object_types_list = network_details.get("object_types", [])
            obj_type_detail_map = {}
            for obj_type_detail in object_types_list:
                obj_type_id = obj_type_detail.get("id")
                if obj_type_id:
                    primary_keys = obj_type_detail.get("primary_keys", [])
                    if not primary_keys:
                        primary_key_field = obj_type_detail.get("primary_key_field")
                        if primary_key_field:
                            primary_keys = [primary_key_field]

                    obj_type_detail_map[obj_type_id] = {
                        "concept_id": obj_type_id,
                        "concept_name": obj_type_detail.get("name", ""),
                        "data_properties": obj_type_detail.get("data_properties", []),
                        "primary_keys": primary_keys,
                        "display_key": obj_type_detail.get("display_key"),
                    }

            for obj in filtered_objects.values():
                obj_type_id = obj.get("id")
                if obj_type_id in obj_type_detail_map:
                    schema_object_types.append(obj_type_detail_map[obj_type_id])
                else:
                    schema_object_types.append(
                        {
                            "concept_id": obj_type_id,
                            "concept_name": obj.get("name", ""),
                            "data_properties": obj.get("data_properties", []),
                            "primary_keys": [],
                            "display_key": None,
                        }
                    )

        schema_relation_types = []
        if filtered_relations:
            for rel in filtered_relations:
                schema_relation_types.append(
                    {
                        "concept_id": rel.get("concept_id") or rel.get("id", ""),
                        "concept_name": rel.get("concept_name") or rel.get("name", ""),
                        "source_object_type_id": rel.get("source_object_type_id", ""),
                        "target_object_type_id": rel.get("target_object_type_id", ""),
                    }
                )

        schema_info = {"object_types": schema_object_types, "relation_types": schema_relation_types}
        logger.debug(
            f"构建新的schema_info，"
            f"对象类型: {len(schema_object_types)} 项，"
            f"关系类型: {len(schema_relation_types)} 项"
        )
        return schema_info

    # 从 session 获取了 schema_info：补齐当前轮次的对象类型（使用 network_details 的完整信息）
    if network_details and filtered_objects and isinstance(network_details, dict):
        object_types_list = network_details.get("object_types", [])
        obj_type_detail_map = {}
        for obj_type_detail in object_types_list:
            obj_type_id = obj_type_detail.get("id")
            if obj_type_id:
                primary_keys = obj_type_detail.get("primary_keys", [])
                if not primary_keys:
                    primary_key_field = obj_type_detail.get("primary_key_field")
                    if primary_key_field:
                        primary_keys = [primary_key_field]

                obj_type_detail_map[obj_type_id] = {
                    "concept_id": obj_type_id,
                    "concept_name": obj_type_detail.get("name", ""),
                    "data_properties": obj_type_detail.get("data_properties", []),
                    "primary_keys": primary_keys,
                    "display_key": obj_type_detail.get("display_key"),
                }

        existing_obj_type_ids = {obj.get("concept_id") for obj in schema_info.get("object_types", [])}
        for obj in filtered_objects.values():
            obj_type_id = obj.get("id")
            if obj_type_id in obj_type_detail_map and obj_type_id not in existing_obj_type_ids:
                schema_info["object_types"].append(obj_type_detail_map[obj_type_id])
                logger.debug(f"补充对象类型 {obj_type_id} 到schema_info")

    return schema_info


