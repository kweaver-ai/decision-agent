# -*- coding: utf-8 -*-
"""
检索历史/Schema 相关的会话能力
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple

from data_retrieval.logs.logger import logger

from ._base import _SessionBase


class _RetrievalHistoryMixin(_SessionBase):
    @classmethod
    def _get_rounds_for_kn(cls, records: List[Dict[str, Any]]) -> Set[int]:
        rounds: Set[int] = set()
        for record in records:
            if "round" in record:
                rounds.add(record["round"])
        return rounds

    @classmethod
    def get_session_count(cls) -> int:
        return len(cls._session_records)

    @classmethod
    def get_session_info(cls) -> Dict[str, Any]:
        session_count = len(cls._session_records)
        total_records = sum(
            sum(len(kn_data.get("retrieval_results", [])) for kn_data in kn_dict.values())
            for kn_dict in cls._session_records.values()
        )
        total_relation_scores = sum(
            sum(len(kn_data.get("relation_scores", {})) for kn_data in kn_dict.values())
            for kn_dict in cls._session_records.values()
        )
        total_property_scores = sum(
            sum(len(kn_data.get("property_scores", {})) for kn_data in kn_dict.values())
            for kn_dict in cls._session_records.values()
        )

        return {
            "active_sessions": session_count,
            "total_records": total_records,
            "total_relation_scores": total_relation_scores,
            "total_property_scores": total_property_scores,
            "expire_minutes": cls.SESSION_EXPIRE_MINUTES,
        }

    @classmethod
    def add_retrieval_record(cls, session_id: str, kn_id: str, retrieval_results: List[Dict[str, Any]]) -> None:
        if not session_id:
            logger.debug(f"session_id为空，跳过存储 {len(retrieval_results)} 条检索结果")
            return

        cls._update_session_access_time(session_id)
        cls._ensure_kn_record(session_id, kn_id)

        # 计算当前轮次
        current_round = len(cls._get_rounds_for_kn(cls._session_records[session_id][kn_id]["retrieval_results"])) + 1

        results_with_round = []
        for result in retrieval_results:
            result_copy = result.copy()
            result_copy["round"] = current_round
            results_with_round.append(result_copy)

        cls._session_records[session_id][kn_id]["retrieval_results"].extend(results_with_round)
        logger.info(f"会话 {session_id} 的知识网络 {kn_id} 第{current_round}轮添加了 {len(retrieval_results)} 条检索记录")

    @classmethod
    def get_retrieval_history(cls, session_id: str, kn_id: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        if session_id not in cls._session_records:
            return {}

        cls._update_session_access_time(session_id)

        if kn_id:
            if kn_id in cls._session_records[session_id]:
                return {kn_id: cls._session_records[session_id][kn_id].get("retrieval_results", [])}
            return {kn_id: []}

        result: Dict[str, List[Dict[str, Any]]] = {}
        for kn_id_iter, kn_data in cls._session_records[session_id].items():
            result[kn_id_iter] = kn_data.get("retrieval_results", [])
        return result

    @classmethod
    def get_all_rounds_union(cls, session_id: str, kn_id: str) -> List[Dict[str, Any]]:
        if (session_id not in cls._session_records) or (kn_id not in cls._session_records[session_id]):
            return []

        cls._update_session_access_time(session_id)

        all_records = cls._session_records[session_id][kn_id].get("retrieval_results", [])
        # 目标：
        # - schema 维度：按 (concept_id, concept_type) 取“最新字段”
        # - 语义实例 nodes 维度：由 _SemanticNodesMixin 独立维护（不绑定在 object_types 下）
        acc: Dict[Tuple[str, str], Dict[str, Any]] = {}
        order: List[Tuple[str, str]] = []

        for record in all_records:
            concept_id = (record.get("concept_id", "") or "").strip()
            concept_type = (record.get("concept_type", "") or "").strip()
            key = (concept_id, concept_type)

            if key not in acc:
                order.append(key)
                acc[key] = {
                    "concept_type": concept_type,
                    "concept_id": concept_id,
                    "concept_name": record.get("concept_name", ""),
                }

            # 最新字段覆盖（名称/描述等）
            if "concept_name" in record:
                acc[key]["concept_name"] = record.get("concept_name", acc[key].get("concept_name", ""))
            if "comment" in record:
                acc[key]["comment"] = record.get("comment")

            if concept_type == "object_type":
                # schema 字段：跟随最新一轮
                if "data_properties" in record:
                    acc[key]["data_properties"] = record.get("data_properties", [])
                if "logic_properties" in record:
                    acc[key]["logic_properties"] = record.get("logic_properties", [])
                if "primary_keys" in record:
                    acc[key]["primary_keys"] = record.get("primary_keys", [])
                elif "primary_key_field" in record:
                    pkf = record.get("primary_key_field")
                    if pkf:
                        acc[key]["primary_keys"] = [pkf]
                if "display_key" in record:
                    acc[key]["display_key"] = record.get("display_key")
                if "sample_data" in record:
                    acc[key]["sample_data"] = record.get("sample_data")

            else:
                if "source_object_type_id" in record:
                    acc[key]["source_object_type_id"] = record.get("source_object_type_id")
                if "target_object_type_id" in record:
                    acc[key]["target_object_type_id"] = record.get("target_object_type_id")

        return [acc[k] for k in order]

    @classmethod
    def get_previous_rounds_union(
        cls, session_id: str, kn_id: str, exclude_current_round: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        if (session_id not in cls._session_records) or (kn_id not in cls._session_records[session_id]):
            return []

        cls._update_session_access_time(session_id)

        all_records = cls._session_records[session_id][kn_id].get("retrieval_results", [])

        if exclude_current_round is None:
            all_rounds = cls._get_rounds_for_kn(all_records)
            exclude_current_round = max(all_rounds) if all_rounds else -1

        previous_records = [r for r in all_records if r.get("round") != exclude_current_round]
        # 与 get_all_rounds_union 保持一致：previous_records 内做 schema 最新覆盖
        acc: Dict[Tuple[str, str], Dict[str, Any]] = {}
        order: List[Tuple[str, str]] = []

        for record in previous_records:
            concept_id = (record.get("concept_id", "") or "").strip()
            concept_type = (record.get("concept_type", "") or "").strip()
            key = (concept_id, concept_type)

            if key not in acc:
                order.append(key)
                acc[key] = {
                    "concept_type": concept_type,
                    "concept_id": concept_id,
                    "concept_name": record.get("concept_name", ""),
                }

            if "concept_name" in record:
                acc[key]["concept_name"] = record.get("concept_name", acc[key].get("concept_name", ""))
            if "comment" in record:
                acc[key]["comment"] = record.get("comment")

            if concept_type == "object_type":
                if "data_properties" in record:
                    acc[key]["data_properties"] = record.get("data_properties", [])
                if "logic_properties" in record:
                    acc[key]["logic_properties"] = record.get("logic_properties", [])
                if "primary_keys" in record:
                    acc[key]["primary_keys"] = record.get("primary_keys", [])
                elif "primary_key_field" in record:
                    pkf = record.get("primary_key_field")
                    if pkf:
                        acc[key]["primary_keys"] = [pkf]
                if "display_key" in record:
                    acc[key]["display_key"] = record.get("display_key")
                if "sample_data" in record:
                    acc[key]["sample_data"] = record.get("sample_data")

            else:
                if "source_object_type_id" in record:
                    acc[key]["source_object_type_id"] = record.get("source_object_type_id")
                if "target_object_type_id" in record:
                    acc[key]["target_object_type_id"] = record.get("target_object_type_id")

        return [acc[k] for k in order]

    @classmethod
    def get_retrieved_concept_ids(cls, session_id: str, kn_id: Optional[str] = None) -> List[Dict[str, Any]]:
        history = cls.get_retrieval_history(session_id, kn_id)
        result = []

        for history_kn_id, records in history.items():
            for record in records:
                record_with_kn_id = record.copy()
                record_with_kn_id["kn_id"] = history_kn_id
                result.append(record_with_kn_id)

        return result

    @classmethod
    def clear_session(cls, session_id: str) -> None:
        cls._session_records.pop(session_id, None)
        cls._session_last_access.pop(session_id, None)
        logger.info(f"已清除会话 {session_id} 的所有记录")

    @classmethod
    def clear_knowledge_network_records(cls, session_id: str, kn_id: str) -> None:
        if session_id in cls._session_records and kn_id in cls._session_records[session_id]:
            del cls._session_records[session_id][kn_id]
            logger.info(f"已清除会话 {session_id} 中知识网络 {kn_id} 的记录")

    @classmethod
    def extend_session_ttl(cls, session_id: str, extend_minutes: int = 30) -> bool:
        if session_id not in cls._session_records:
            return False
        cls._update_session_access_time(session_id)
        logger.info(f"已延长会话 {session_id} 的有效期 {extend_minutes} 分钟")
        return True

    @classmethod
    def get_schema_info(cls, session_id: str, kn_id: str) -> Optional[Dict[str, Any]]:
        if (session_id not in cls._session_records) or (kn_id not in cls._session_records[session_id]):
            return None

        cls._update_session_access_time(session_id)

        all_rounds_union = cls.get_all_rounds_union(session_id, kn_id)
        if not all_rounds_union:
            return None

        object_types = [i for i in all_rounds_union if i.get("concept_type") == "object_type"]
        relation_types = [i for i in all_rounds_union if i.get("concept_type") == "relation_type"]

        return {"object_types": object_types, "relation_types": relation_types}

    @classmethod
    def has_schema_info(cls, session_id: str, kn_id: str) -> bool:
        schema_info = cls.get_schema_info(session_id, kn_id)
        return schema_info is not None and (
            len(schema_info.get("object_types", [])) > 0 or len(schema_info.get("relation_types", [])) > 0
        )


