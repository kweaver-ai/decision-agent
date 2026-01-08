# -*- coding: utf-8 -*-
"""
语义实例召回：多对象类型并发调度与实例 map 后处理

目标：
- 把 `semantic_instance_retrieval.py` 中与“并发调度/汇总”相关的通用逻辑抽离
- 让主类文件更多扮演 pipeline orchestrator 的角色
"""

from __future__ import annotations

import asyncio
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple

from data_retrieval.logs.logger import logger


RetrieveFn = Callable[[Dict[str, Any]], Awaitable[List[Dict[str, Any]]]]
RerankFn = Callable[[str, List[Dict[str, Any]]], Awaitable[Tuple[str, List[Dict[str, Any]]]]]


def _get_object_type_id(obj_type: Dict[str, Any]) -> Optional[str]:
    return obj_type.get("concept_id") or obj_type.get("id")


async def retrieve_map_for_all_object_types(
    *,
    object_types: List[Dict[str, Any]],
    retrieve_one: RetrieveFn,
    max_concurrent: int,
    log_prefix: str,
    swallow_exceptions: bool = True,
) -> Dict[str, List[Dict[str, Any]]]:
    """
    对所有对象类型并发执行 retrieve_one，并返回 {object_type_id: instances}。
    失败时保证该 object_type_id 对应空列表。
    """
    if not object_types:
        return {}

    logger.info(
        f"{log_prefix}：开始并发执行，共 {len(object_types)} 个对象类型，max_concurrent={max_concurrent}，"
        f"swallow_exceptions={swallow_exceptions}"
    )
    semaphore = asyncio.Semaphore(max_concurrent)

    async def _wrapped(obj_type: Dict[str, Any]) -> List[Dict[str, Any]]:
        async with semaphore:
            if not swallow_exceptions:
                return await retrieve_one(obj_type)
            try:
                return await retrieve_one(obj_type)
            except Exception as e:
                logger.warning(
                    f"{log_prefix}：对象类型 {_get_object_type_id(obj_type)} 执行失败: {str(e)}",
                    exc_info=True,
                )
                return []

    tasks = [_wrapped(obj_type) for obj_type in object_types]
    results = await asyncio.gather(*tasks, return_exceptions=swallow_exceptions)

    instance_map: Dict[str, List[Dict[str, Any]]] = {}
    success_count = 0
    fail_or_empty_count = 0

    for obj_type, result in zip(object_types, results):
        object_type_id = _get_object_type_id(obj_type)
        if not object_type_id:
            continue

        if isinstance(result, Exception):
            logger.warning(f"{log_prefix}：对象类型 {object_type_id} 执行失败: {str(result)}")
            instance_map[object_type_id] = []
            fail_or_empty_count += 1
            continue

        instance_map[object_type_id] = result or []
        if result:
            success_count += 1
        else:
            fail_or_empty_count += 1

    logger.info(
        f"{log_prefix}：完成。成功(有数据)={success_count}，失败或无数据={fail_or_empty_count}，总计={len(object_types)}"
    )
    return instance_map


async def rerank_instance_map(
    *,
    instance_map: Dict[str, List[Dict[str, Any]]],
    rerank_one: RerankFn,
) -> Dict[str, List[Dict[str, Any]]]:
    """
    对候选实例 map 做统一 rerank（按对象类型分别 rerank）。
    任一对象类型 rerank 抛错则整体抛错（沿用旧行为）。
    """
    if not instance_map:
        return {}

    tasks = [rerank_one(obj_type_id, insts) for obj_type_id, insts in instance_map.items()]
    pairs = await asyncio.gather(*tasks)  # 不吞异常：任一失败直接抛
    return {obj_id: insts for obj_id, insts in pairs}


