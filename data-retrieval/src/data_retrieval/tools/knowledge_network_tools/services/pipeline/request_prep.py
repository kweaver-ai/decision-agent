# -*- coding: utf-8 -*-
"""
检索请求参数归一化（pipeline 纯函数）
"""

from __future__ import annotations

from typing import Any, List, Optional

from ...models import RetrievalConfig


def normalize_kn_ids(kn_ids: List[Any]) -> List[str]:
    """
    将 kn_ids 归一化为 kn_id_list（只取 knowledge_network_id）。

    支持：
    - dict: {"knowledge_network_id": "..."}
    - Pydantic 对象：obj.knowledge_network_id
    - str（历史写法）：直接作为 kn_id
    """
    if not kn_ids:
        raise ValueError("kn_ids参数不能为空，必须提供至少一个知识网络配置")

    kn_id_list: List[str] = []
    for item in kn_ids:
        if isinstance(item, str):
            kn_id_list.append(item)
            continue
        if isinstance(item, dict):
            kn_id = item.get("knowledge_network_id")
            if not kn_id:
                raise ValueError("kn_ids配置中必须包含knowledge_network_id字段")
            kn_id_list.append(kn_id)
            continue

        kn_id = getattr(item, "knowledge_network_id", None)
        if not kn_id:
            raise ValueError("kn_ids配置中必须包含knowledge_network_id字段")
        kn_id_list.append(kn_id)

    return kn_id_list


def normalize_retrieval_config(retrieval_config: Optional[Any]) -> RetrievalConfig:
    """
    将 retrieval_config 归一化为 RetrievalConfig。
    - None：使用默认值
    - dict：作为 pydantic 入参构造
    - RetrievalConfig：直接返回
    """
    if retrieval_config is None:
        return RetrievalConfig()
    if isinstance(retrieval_config, dict):
        return RetrievalConfig(**retrieval_config)
    if isinstance(retrieval_config, RetrievalConfig):
        return retrieval_config
    # 容错：让上游尽早报错
    raise TypeError(f"retrieval_config 类型不支持: {type(retrieval_config)}")


