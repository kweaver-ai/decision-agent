# -*- coding: utf-8 -*-
"""
样例数据（sample_data）相关的会话能力
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from data_retrieval.logs.logger import logger

from ._base import _SessionBase


class _SampleDataMixin(_SessionBase):
    @classmethod
    def set_sample_data(
        cls, session_id: str, kn_id: str, object_type_id: str, sample_data: Optional[Dict[str, Any]]
    ) -> None:
        if not session_id:
            return
        cls._update_session_access_time(session_id)
        cls._ensure_kn_record(session_id, kn_id)

        cls._session_records[session_id][kn_id]["sample_data"][object_type_id] = {
            "sample_data": sample_data,
            "fetch_time": datetime.now().isoformat(),
        }
        logger.debug(f"会话 {session_id} 的知识网络 {kn_id} 对象类型 {object_type_id} 的样例数据已存储")

    @classmethod
    def get_sample_data(cls, session_id: str, kn_id: str, object_type_id: str) -> Optional[Dict[str, Any]]:
        if (
            session_id not in cls._session_records
            or kn_id not in cls._session_records[session_id]
            or object_type_id not in cls._session_records[session_id][kn_id].get("sample_data", {})
        ):
            return None

        cls._update_session_access_time(session_id)
        sample_data_info = cls._session_records[session_id][kn_id]["sample_data"][object_type_id]
        return sample_data_info.get("sample_data")

    @classmethod
    def get_all_sample_data(cls, session_id: str, kn_id: str) -> Dict[str, Optional[Dict[str, Any]]]:
        if session_id not in cls._session_records or kn_id not in cls._session_records[session_id]:
            return {}

        sample_data_map = cls._session_records[session_id][kn_id].get("sample_data", {})
        if not isinstance(sample_data_map, dict):
            return {}

        cls._update_session_access_time(session_id)
        return {object_type_id: info.get("sample_data") for object_type_id, info in sample_data_map.items()}

    @classmethod
    def has_sample_data(cls, session_id: str, kn_id: str) -> bool:
        if session_id not in cls._session_records or kn_id not in cls._session_records[session_id]:
            return False
        sample_data = cls._session_records[session_id][kn_id].get("sample_data", {})
        return isinstance(sample_data, dict) and len(sample_data) > 0

    @classmethod
    def set_all_sample_data(
        cls, session_id: str, kn_id: str, sample_data_dict: Dict[str, Optional[Dict[str, Any]]]
    ) -> None:
        if not session_id:
            return
        cls._update_session_access_time(session_id)
        cls._ensure_kn_record(session_id, kn_id)

        fetch_time = datetime.now().isoformat()
        for object_type_id, sample_data in sample_data_dict.items():
            cls._session_records[session_id][kn_id]["sample_data"][object_type_id] = {
                "sample_data": sample_data,
                "fetch_time": fetch_time,
            }

        logger.info(f"会话 {session_id} 的知识网络 {kn_id} 批量存储了 {len(sample_data_dict)} 个对象类型的样例数据")


