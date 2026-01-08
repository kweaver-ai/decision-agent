# -*- coding: utf-8 -*-
"""
概念召回 / 语义实例召回 的缓存能力
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from data_retrieval.logs.logger import logger

from ._base import _SessionBase


class _CacheMixin(_SessionBase):
    # ==================== 概念召回缓存 ====================
    @classmethod
    def has_concept_retrieval_cache(cls, session_id: str, kn_id: str, query: str) -> bool:
        if not session_id or not kn_id or not query:
            return False
        if session_id not in cls._session_records or kn_id not in cls._session_records[session_id]:
            return False
        cache_key = f"{session_id}:{kn_id}:{query}"
        concept_cache = cls._session_records[session_id][kn_id].get("concept_retrieval_cache", {})
        return cache_key in concept_cache

    @classmethod
    def get_concept_retrieval_cache(cls, session_id: str, kn_id: str, query: str) -> Optional[Dict[str, Any]]:
        if not session_id or not kn_id or not query:
            return None
        if session_id not in cls._session_records or kn_id not in cls._session_records[session_id]:
            return None
        cache_key = f"{session_id}:{kn_id}:{query}"
        concept_cache = cls._session_records[session_id][kn_id].get("concept_retrieval_cache", {})
        if cache_key in concept_cache:
            cls._update_session_access_time(session_id)
            return concept_cache[cache_key]
        return None

    @classmethod
    def set_concept_retrieval_cache(
        cls, session_id: str, kn_id: str, query: str, relevant_concepts: Tuple[Any, Any], network_details: Dict[str, Any]
    ) -> None:
        if not session_id or not kn_id or not query:
            return
        cls._update_session_access_time(session_id)
        cls._ensure_kn_record(session_id, kn_id)
        cache_key = f"{session_id}:{kn_id}:{query}"
        cls._session_records[session_id][kn_id]["concept_retrieval_cache"][cache_key] = {
            "query": query,
            "relevant_concepts": relevant_concepts,
            "network_details": network_details,
            "timestamp": datetime.now(),
        }
        logger.debug(f"已缓存概念召回结果，session_id={session_id}, kn_id={kn_id}, query={query[:50]}...")

    # ==================== 语义实例召回缓存 ====================
    @classmethod
    def has_semantic_instance_cache(cls, session_id: str, kn_id: str, query: str) -> bool:
        if not session_id or not kn_id or not query:
            return False
        if session_id not in cls._session_records or kn_id not in cls._session_records[session_id]:
            return False
        cache_key = f"{session_id}:{kn_id}:{query}"
        semantic_cache = cls._session_records[session_id][kn_id].get("semantic_instance_cache", {})
        return cache_key in semantic_cache

    @classmethod
    def get_semantic_instance_cache(cls, session_id: str, kn_id: str, query: str) -> Optional[Dict[str, Any]]:
        if not session_id or not kn_id or not query:
            return None
        if session_id not in cls._session_records or kn_id not in cls._session_records[session_id]:
            return None
        cache_key = f"{session_id}:{kn_id}:{query}"
        semantic_cache = cls._session_records[session_id][kn_id].get("semantic_instance_cache", {})
        if cache_key in semantic_cache:
            cls._update_session_access_time(session_id)
            return semantic_cache[cache_key]
        return None

    @classmethod
    def set_semantic_instance_cache(cls, session_id: str, kn_id: str, query: str, semantic_instances_map: Dict[str, Any]) -> None:
        if not session_id or not kn_id or not query:
            return
        cls._update_session_access_time(session_id)
        cls._ensure_kn_record(session_id, kn_id)
        cache_key = f"{session_id}:{kn_id}:{query}"
        cls._session_records[session_id][kn_id]["semantic_instance_cache"][cache_key] = {
            "query": query,
            "semantic_instances_map": semantic_instances_map,
            "timestamp": datetime.now(),
        }
        logger.debug(f"已缓存语义实例召回结果，session_id={session_id}, kn_id={kn_id}, query={query[:50]}...")


