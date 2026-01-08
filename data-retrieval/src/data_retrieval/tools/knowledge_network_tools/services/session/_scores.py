# -*- coding: utf-8 -*-
"""
关系/属性打分相关的会话能力
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from data_retrieval.logs.logger import logger

from ._base import _SessionBase


class _ScoresMixin(_SessionBase):
    @classmethod
    def clear_relation_scores(cls, session_id: str, kn_id: str) -> None:
        if session_id in cls._session_records and kn_id in cls._session_records[session_id]:
            cls._session_records[session_id][kn_id]["relation_scores"] = {}
            logger.info(f"已清除会话 {session_id} 中知识网络 {kn_id} 的关系路径分数")

    @classmethod
    def clear_property_scores(cls, session_id: str, kn_id: str) -> None:
        if session_id in cls._session_records and kn_id in cls._session_records[session_id]:
            cls._session_records[session_id][kn_id]["property_scores"] = {}
            logger.info(f"已清除会话 {session_id} 中知识网络 {kn_id} 的属性分数")

    @classmethod
    def add_relation_score(cls, session_id: str, kn_id: str, relation_id: str, score: float) -> None:
        if not session_id:
            return
        cls._update_session_access_time(session_id)
        cls._ensure_kn_record(session_id, kn_id)
        cls._session_records[session_id][kn_id]["relation_scores"][relation_id] = score

    @classmethod
    def add_property_score(cls, session_id: str, kn_id: str, property_id: str, score: float) -> None:
        if not session_id:
            return
        cls._update_session_access_time(session_id)
        cls._ensure_kn_record(session_id, kn_id)
        cls._session_records[session_id][kn_id]["property_scores"][property_id] = score

    @classmethod
    def get_relation_score(cls, session_id: str, kn_id: str, relation_id: str) -> Optional[float]:
        if (
            session_id not in cls._session_records
            or kn_id not in cls._session_records[session_id]
            or relation_id not in cls._session_records[session_id][kn_id]["relation_scores"]
        ):
            return None
        cls._update_session_access_time(session_id)
        return cls._session_records[session_id][kn_id]["relation_scores"][relation_id]

    @classmethod
    def get_property_score(cls, session_id: str, kn_id: str, property_id: str) -> Optional[float]:
        if (
            session_id not in cls._session_records
            or kn_id not in cls._session_records[session_id]
            or property_id not in cls._session_records[session_id][kn_id]["property_scores"]
        ):
            return None
        cls._update_session_access_time(session_id)
        return cls._session_records[session_id][kn_id]["property_scores"][property_id]

    @classmethod
    def get_all_relation_scores(cls, session_id: str, kn_id: str) -> Dict[str, float]:
        if session_id not in cls._session_records or kn_id not in cls._session_records[session_id]:
            return {}
        cls._update_session_access_time(session_id)
        return cls._session_records[session_id][kn_id]["relation_scores"].copy()

    @classmethod
    def get_all_property_scores(cls, session_id: str, kn_id: str) -> Dict[str, float]:
        if session_id not in cls._session_records or kn_id not in cls._session_records[session_id]:
            return {}
        cls._update_session_access_time(session_id)
        return cls._session_records[session_id][kn_id]["property_scores"].copy()


