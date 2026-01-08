# -*- coding: utf-8 -*-
"""
样例数据（sample_data）获取逻辑

从 `retrieval_tool.py` 中抽离出来，避免主编排文件过长。
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional

import httpx

from data_retrieval.logs.logger import logger

from ...config import config


async def fetch_sample_data_for_object_type(
    kn_id: str,
    object_type_id: str,
    headers: Optional[Dict[str, str]] = None,
) -> Optional[Dict[str, Any]]:
    """
    获取单个对象类型的样例数据（最多1条）。
    """
    try:
        url = f"{config.KNOWLEDGE_NETWORK_QUERY_API_BASE}/knowledge-networks/{kn_id}/object-types/{object_type_id}"

        request_headers = {"X-HTTP-Method-Override": "GET", "Content-Type": "application/json"}
        if headers:
            request_headers.update(headers)

        request_body = {"limit": 1}

        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.post(url, headers=request_headers, json=request_body)
            response.raise_for_status()
            result = response.json()

            datas = result.get("datas", [])
            if datas and len(datas) > 0:
                return datas[0]

            logger.debug(f"对象类型 {object_type_id} 没有数据，返回None")
            return None

    except httpx.HTTPStatusError as e:
        logger.warning(f"获取对象类型 {object_type_id} 的样例数据失败: HTTP {e.response.status_code}", exc_info=True)
        return None
    except Exception as e:
        logger.warning(f"获取对象类型 {object_type_id} 的样例数据失败: {str(e)}", exc_info=True)
        return None


async def fetch_all_sample_data(
    kn_id: str,
    object_types: List[Dict[str, Any]],
    headers: Optional[Dict[str, str]] = None,
    max_concurrent: int = 10,
) -> Dict[str, Optional[Dict[str, Any]]]:
    """
    并发获取多个对象类型的样例数据。

    返回格式：{object_type_id: sample_data}
    """
    if not object_types:
        return {}

    object_type_ids: List[str] = []
    for obj_type in object_types:
        obj_id = obj_type.get("id") or obj_type.get("concept_id")
        if obj_id:
            object_type_ids.append(obj_id)

    if not object_type_ids:
        logger.warning("没有找到有效的对象类型ID")
        return {}

    logger.info(f"开始并发获取 {len(object_type_ids)} 个对象类型的样例数据")

    semaphore = asyncio.Semaphore(max_concurrent)

    async def fetch_with_semaphore(object_type_id: str):
        async with semaphore:
            return await fetch_sample_data_for_object_type(kn_id, object_type_id, headers)

    tasks = [fetch_with_semaphore(obj_id) for obj_id in object_type_ids]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    sample_data_dict: Dict[str, Optional[Dict[str, Any]]] = {}
    success_count = 0
    fail_count = 0

    for object_type_id, result in zip(object_type_ids, results):
        if isinstance(result, Exception):
            logger.warning(f"获取对象类型 {object_type_id} 的样例数据失败: {str(result)}")
            sample_data_dict[object_type_id] = None
            fail_count += 1
        else:
            sample_data_dict[object_type_id] = result
            if result is not None:
                success_count += 1
            else:
                fail_count += 1

    logger.info(f"样例数据获取完成，成功: {success_count}, 失败或无数据: {fail_count}, 总计: {len(object_type_ids)}")
    return sample_data_dict


