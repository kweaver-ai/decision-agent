# -*- coding: utf-8 -*-
"""
语义实例召回：关系路径 API 调用

从 `semantic_instance_retrieval.py` 抽离，降低单文件长度。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set

from data_retrieval.logs.logger import logger

from ...infra.clients.http_client import KnowledgeNetworkHTTPClient


async def call_relation_path_api(
    *,
    kn_id: str,
    relation_type_paths: List[Dict[str, Any]],
    headers: Optional[Dict[str, str]] = None,
    timeout: float = 10.0,
) -> Optional[Dict[str, Any]]:
    """调用关系路径检索API"""
    try:
        request_body = {"relation_type_paths": relation_type_paths}
        return await KnowledgeNetworkHTTPClient.query_relation_path(
            kn_id=kn_id,
            relation_type_paths=request_body,
            headers=headers,
            timeout=timeout,
        )
    except Exception as e:
        logger.warning(f"调用关系路径检索API失败 (kn_id={kn_id}): {str(e)}", exc_info=True)
        return None




