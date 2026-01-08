# -*- coding: utf-8 -*-
"""
会话管理基础能力（内存存储 + TTL + 初始化结构）

注意：此处使用 classmethod + 类变量的方式，保持与历史实现一致（全局内存会话池）。
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict

from data_retrieval.logs.logger import logger


class _SessionBase:
    """
    会话基础类：
    - 维护内存中的 session 记录与 last_access
    - 提供 TTL 清理与 kn 记录结构初始化
    """

    # 格式:
    # {session_id: {kn_id: {"retrieval_results": [...], "relation_scores": {...}, ...}}}
    _session_records: Dict[str, Dict[str, Dict[str, Any]]] = {}
    _session_last_access: Dict[str, datetime] = {}

    # 会话失效时间（分钟）
    SESSION_EXPIRE_MINUTES = 10

    @classmethod
    def _update_session_access_time(cls, session_id: str) -> None:
        """更新会话的最后访问时间"""
        if not session_id:
            return
        cls._session_last_access[session_id] = datetime.now()

    @classmethod
    def _clean_expired_sessions(cls) -> None:
        """清理过期会话"""
        current_time = datetime.now()
        expired_sessions = []

        for session_id, last_access in list(cls._session_last_access.items()):
            if current_time - last_access > timedelta(minutes=cls.SESSION_EXPIRE_MINUTES):
                expired_sessions.append(session_id)

        for session_id in expired_sessions:
            cls._session_records.pop(session_id, None)
            cls._session_last_access.pop(session_id, None)
            logger.info(f"已清理过期会话 {session_id}")

        if expired_sessions:
            logger.info(f"共清理了 {len(expired_sessions)} 个过期会话")

    @classmethod
    def _ensure_kn_record(cls, session_id: str, kn_id: str) -> None:
        """
        确保 session_id/kn_id 对应的记录结构存在。

        这里统一初始化所有字段，避免不同方法各自初始化导致结构不一致。
        """
        if session_id not in cls._session_records:
            cls._session_records[session_id] = {}

        if kn_id not in cls._session_records[session_id]:
            cls._session_records[session_id][kn_id] = {
                "retrieval_results": [],
                "relation_scores": {},
                "property_scores": {},
                "sample_data": {},
                "semantic_nodes_results": [],
                "concept_retrieval_cache": {},
                "semantic_instance_cache": {},
            }
        else:
            # 补齐缺失键（兼容历史部分结构缺字段的情况）
            rec = cls._session_records[session_id][kn_id]
            rec.setdefault("retrieval_results", [])
            rec.setdefault("relation_scores", {})
            rec.setdefault("property_scores", {})
            rec.setdefault("sample_data", {})
            rec.setdefault("semantic_nodes_results", [])
            rec.setdefault("concept_retrieval_cache", {})
            rec.setdefault("semantic_instance_cache", {})


