# -*- coding: utf-8 -*-
"""
Schema 输出裁剪（精简模式）

从 `retrieval_tool.py` 抽离，便于集中管理 schema 输出策略。
"""

from __future__ import annotations

from typing import Any, Dict


def to_brief_schema(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    将schema结果压缩为精简格式，仅保留必要字段。
    """
    object_types = []
    for obj in result.get("object_types", []):
        props = obj.get("data_properties") or []
        logic_props = obj.get("logic_properties") or []

        def _name_pairs(items):
            pairs = []
            for p in items:
                name = (p.get("name") or "").strip()
                dname = (p.get("display_name") or "").strip()
                if not name and not dname:
                    continue
                # 构建精简属性对象，包含 name, display_name, type 和 condition_operations
                prop_dict = {}
                if name:
                    prop_dict["name"] = name
                if dname:
                    prop_dict["display_name"] = dname
                # 始终保留 type 字段（如果存在）
                if "type" in p:
                    prop_dict["type"] = p.get("type")
                # 始终保留 condition_operations 字段（即使为空列表也要保留）
                if "condition_operations" in p:
                    prop_dict["condition_operations"] = p.get("condition_operations")
                pairs.append(prop_dict)
            return pairs

        brief_obj = {"concept_id": obj.get("concept_id"), "concept_name": obj.get("concept_name")}

        comment = (obj.get("comment") or "").strip()
        if comment:
            brief_obj["comment"] = comment

        prop_pairs = _name_pairs(props)
        if prop_pairs:
            brief_obj["data_properties"] = prop_pairs

        logic_pairs = _name_pairs(logic_props)
        if logic_pairs:
            brief_obj["logic_properties"] = logic_pairs

        # 保留 sample_data 字段（如果存在，即使为 None 也保留，表示 include_sample_data=True）
        # 精简模式下需要移除 sample_data 中的 _score 字段
        sample_data = None
        if "sample_data" in obj:
            sample_data = obj.get("sample_data")
            # 如果是字典，移除 _score 字段
            if isinstance(sample_data, dict):
                sample_data = {k: v for k, v in sample_data.items() if k != "_score"}

        # 过滤空值，但保留 sample_data 字段（在过滤后单独添加）
        brief_obj = {k: v for k, v in brief_obj.items() if v not in (None, [], {}, "")}
        
        # 如果原对象中有 sample_data 字段，则保留它（即使为 None 或空字典，表示 include_sample_data=True）
        if "sample_data" in obj:
            brief_obj["sample_data"] = sample_data
        
        object_types.append(brief_obj)

    relation_types = []
    for rel in result.get("relation_types", []):
        brief_rel = {
            "concept_id": rel.get("concept_id"),
            "concept_name": rel.get("concept_name"),
            "source_object_type_id": rel.get("source_object_type_id"),
            "target_object_type_id": rel.get("target_object_type_id"),
        }
        relation_types.append({k: v for k, v in brief_rel.items() if v not in (None, [], {}, "")})

    # 精简模式下的action_types字段过滤：只保留id, name, action_type, object_type_id, object_type_name, comment, tags, kn_id
    brief_action_types = []
    for action in result.get("action_types", []):
        brief_action = {}
        
        # 核心字段：始终保留（即使为空）
        if "id" in action:
            brief_action["id"] = action.get("id")
        if "name" in action:
            brief_action["name"] = action.get("name")
        if "action_type" in action:
            brief_action["action_type"] = action.get("action_type")
        if "object_type_id" in action:
            brief_action["object_type_id"] = action.get("object_type_id")
        
        # 从object_type对象中提取object_type_name
        object_type = action.get("object_type")
        if object_type and isinstance(object_type, dict):
            object_type_name = object_type.get("name")
            if object_type_name:
                brief_action["object_type_name"] = object_type_name
        
        # 保留comment字段（仅非空时保留）
        comment = action.get("comment")
        if comment:
            brief_action["comment"] = comment
        
        # 保留tags字段（仅非空时保留）
        tags = action.get("tags")
        if tags:
            brief_action["tags"] = tags
        
        # 保留kn_id字段（仅非空时保留）
        kn_id = action.get("kn_id")
        if kn_id:
            brief_action["kn_id"] = kn_id
        
        brief_action_types.append(brief_action)
    
    out: Dict[str, Any] = {"object_types": object_types, "relation_types": relation_types, "action_types": brief_action_types}

    # 兼容字段：保留扁平 nodes/message（由上游生成，便于旧消费方）
    if "nodes" in result:
        out["nodes"] = result.get("nodes")
    if "message" in result:
        out["message"] = result.get("message")

    return out


