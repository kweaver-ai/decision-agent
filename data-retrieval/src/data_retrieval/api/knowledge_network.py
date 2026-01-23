# -*- coding: utf-8 -*-
"""
知识网络详情 API

提供获取知识网络详情的功能，用于获取完整的 object_type 到 view_id 映射。
"""

from urllib.parse import urljoin
import traceback

from data_retrieval.api.error import AfDataSourceError
from data_retrieval.api.base import API, HTTPMethod
from data_retrieval.logs.logger import logger

from data_retrieval.settings import get_settings

settings = get_settings()


class KnowledgeNetworkError(Exception):
    """知识网络相关错误"""

    def __init__(self, message: str, original_error: Exception = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)


class KnowledgeNetworkService:
    """知识网络服务"""

    def __init__(self, base_url: str = "", headers: dict = None):
        self.base_url: str = base_url if base_url else settings.KNOWLEDGE_NETWORK_API_BASE
        self.headers: dict = headers or {}
        self._gen_api_url()

    def _gen_api_url(self):
        self.detail_url = urljoin(
            self.base_url,
            "/api/ontology-manager/in/v1/knowledge-networks/{kn_id}"
        )

    def get_detail(self, kn_id: str, headers: dict = None) -> dict:
        """获取知识网络详情（同步）"""
        headers = headers or {}
        headers.update(self.headers)

        url = self.detail_url.format(kn_id=kn_id)
        api = API(
            url=url,
            headers=headers,
            method=HTTPMethod.GET,
            params={"include_detail": "true", "mode": "export"}
        )
        try:
            result = api.call()
            return result
        except AfDataSourceError as e:
            raise KnowledgeNetworkError(f"获取知识网络详情失败: {str(e)}", e) from e

    async def get_detail_async(self, kn_id: str, headers: dict = None) -> dict:
        """获取知识网络详情（异步）"""
        headers = headers or {}
        headers.update(self.headers)

        url = self.detail_url.format(kn_id=kn_id)
        api = API(
            url=url,
            headers=headers,
            method=HTTPMethod.GET,
            params={"include_detail": "true", "mode": "export"}
        )
        try:
            result = await api.call_async()
            return result
        except AfDataSourceError as e:
            raise KnowledgeNetworkError(f"获取知识网络详情失败: {str(e)}", e) from e


async def get_knowledge_network_detail_async(
    kn_id: str,
    headers: dict = None,
    base_url: str = ""
) -> dict:
    """
    获取知识网络详情

    Args:
        kn_id: 知识网络ID
        headers: HTTP请求头
        base_url: 可选的自定义基础URL

    Returns:
        知识网络详情，包含 object_types, relation_types 等信息
    """
    if not kn_id:
        return {}

    try:
        service = KnowledgeNetworkService(base_url=base_url, headers=headers)
        result = await service.get_detail_async(kn_id, headers=headers)
        logger.info(f"获取知识网络详情成功 (kn_id: {kn_id})")
        return result
    except KnowledgeNetworkError:
        traceback.print_exc()
        raise
    except Exception as e:
        traceback.print_exc()
        raise KnowledgeNetworkError(f"获取知识网络详情异常: {str(e)}", e) from e


def build_object_type_view_mapping(kn_detail: dict) -> dict:
    """
    从知识网络详情中构建 object_type_id 到 view_id 的映射

    Args:
        kn_detail: 知识网络详情

    Returns:
        映射字典 {object_type_id: view_id}
    """
    mapping = {}

    object_types = kn_detail.get("object_types", [])
    if not isinstance(object_types, list):
        return mapping

    for obj_type in object_types:
        obj_type_id = obj_type.get("id", "")
        data_source = obj_type.get("data_source", {})
        if data_source.get("type") == "data_view":
            view_id = data_source.get("id", "")
            if obj_type_id and view_id:
                mapping[obj_type_id] = view_id

    logger.debug(f"构建 object_type 到 view_id 映射，共 {len(mapping)} 项")
    return mapping
