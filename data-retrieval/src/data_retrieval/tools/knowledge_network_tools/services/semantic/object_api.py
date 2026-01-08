# -*- coding: utf-8 -*-
"""
语义实例召回：对象实例检索 API 调用
"""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

import httpx

from data_retrieval.logs.logger import logger

from ...infra.clients.http_client import KnowledgeNetworkHTTPClient


async def call_object_retrieval_api(
    *,
    kn_id: str,
    object_type_id: str,
    condition: Dict[str, Any],
    headers: Optional[Dict[str, str]] = None,
    timeout: float = 5.0,
) -> Optional[Dict[str, Any]]:
    """调用对象检索API（语义实例召回场景）。"""
    try:
        return await KnowledgeNetworkHTTPClient.query_object_instances(
            kn_id=kn_id,
            object_type_id=object_type_id,
            condition=condition,
            headers=headers,
            timeout=timeout,
        )
    except httpx.HTTPStatusError as e:
        error_detail = ""
        try:
            if e.response is not None:
                error_detail = f"\n响应状态码: {e.response.status_code}\n响应Body: {e.response.text}"
        except Exception:
            pass

        try:
            request_body_str = f"\n请求Body: {json.dumps(condition, ensure_ascii=False, indent=2)}"
        except Exception:
            try:
                request_body_str = f"\n请求Body: {str(condition)}"
            except Exception:
                request_body_str = "\n请求Body: (无法序列化)"

        logger.warning(
            f"调用对象检索API失败 (kn_id={kn_id}, object_type_id={object_type_id}): {str(e)}{error_detail}{request_body_str}",
            exc_info=True,
        )
        return None
    except Exception as e:
        try:
            request_body_str = f"\n请求Body: {json.dumps(condition, ensure_ascii=False, indent=2)}"
        except Exception:
            try:
                request_body_str = f"\n请求Body: {str(condition)}"
            except Exception:
                request_body_str = "\n请求Body: (无法序列化)"

        logger.warning(
            f"调用对象检索API失败 (kn_id={kn_id}, object_type_id={object_type_id}): {str(e)}{request_body_str}",
            exc_info=True,
        )
        return None


