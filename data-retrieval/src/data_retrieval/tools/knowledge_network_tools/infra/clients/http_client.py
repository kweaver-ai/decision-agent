# -*- coding: utf-8 -*-
"""
HTTP请求模块
处理与知识网络API相关的HTTP请求
"""

import httpx
import json
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
from fastapi import HTTPException
from data_retrieval.logs.logger import logger
from ...config import config
from ...infra.utils.timing_utils import api_timer, add_cost

# 知识网络API基础URL（从配置文件读取）
KNOWLEDGE_NETWORK_API_BASE = config.KNOWLEDGE_NETWORK_API_BASE


class KnowledgeNetworkHTTPClient:
    """知识网络HTTP客户端"""
    
    @classmethod
    async def _make_http_request(cls, url: str, method: str = "GET", params: Optional[Dict[str, Any]] = None, 
                                json_data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None,
                                timeout: float = 30.0) -> Optional[Dict[str, Any]]:
        """
        通用HTTP请求方法
        
        Args:
            url: 请求URL
            method: HTTP方法，默认为GET
            params: 查询参数
            json_data: JSON请求体数据
            headers: HTTP请求头
            
        Returns:
            响应数据或None（如果出错）
        """
        def _safe_dump(obj: Any) -> str:
            """将请求参数/Body安全序列化为字符串（用于错误日志）。"""
            if obj is None:
                return "null"
            try:
                return json.dumps(obj, ensure_ascii=False, indent=2)
            except Exception:
                try:
                    return str(obj)
                except Exception:
                    return "<unserializable>"
        
        def _summarize_headers(h: Dict[str, str]) -> Dict[str, str]:
            """尽量避免打印敏感头；当前仅做最小脱敏。"""
            if not h:
                return {}
            redacted_keys = {"authorization", "cookie", "x-auth-token", "x-api-key"}
            out = {}
            for k, v in h.items():
                if not isinstance(k, str):
                    continue
                if k.lower() in redacted_keys:
                    out[k] = "***"
                else:
                    out[k] = v
            return out
        
        try:
            # 合并默认headers和传入的headers
            request_headers = {}
            if headers:
                request_headers.update(headers)
            # httpx 不接受 header value 为 None；同时尽量保证为 str
            request_headers = {str(k): str(v) for k, v in (request_headers or {}).items() if v is not None}
            
            async with httpx.AsyncClient() as client:
                parsed = urlparse(url)
                path_label = parsed.path or url
                if method.upper() == "GET":
                    include_detail = (params or {}).get("include_detail")
                    is_detail = str(include_detail).lower() == "true"
                    bucket = "detail" if is_detail else "other"
                    label = f"GET {path_label}"
                    with api_timer(bucket, label=label):
                        response = await client.get(
                            url,
                            headers=request_headers,
                            params=params,
                            timeout=timeout
                        )
                elif method.upper() == "POST":
                    bucket = "other"
                    if "/object-types/" in url:
                        bucket = "object_query"
                    elif "/subgraph" in url:
                        bucket = "path_query"
                    query_type = (params or {}).get("query_type")
                    label = f"POST {path_label}" + (f"?query_type={query_type}" if query_type else "")
                    with api_timer(bucket, label=label):
                        response = await client.post(
                            url,
                            headers=request_headers,
                            params=params,
                            json=json_data,
                            timeout=timeout
                        )
                else:
                    raise ValueError(f"不支持的HTTP方法: {method}")
                
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPStatusError as e:
            status = e.response.status_code if e.response is not None else "unknown"
            resp_text = ""
            try:
                resp_text = e.response.text if e.response is not None else ""
            except Exception:
                resp_text = ""
            
            logger.error(
                "HTTP状态错误：%s\n"
                "URL: %s\n"
                "Method: %s\n"
                "Params: %s\n"
                "Request-Headers: %s\n"
                "Request-Body: %s\n"
                "Response-Body: %s",
                status,
                url,
                method,
                _safe_dump(params),
                _safe_dump(_summarize_headers(request_headers)),
                _safe_dump(json_data),
                resp_text,
                exc_info=True
            )
            return None
        except httpx.RequestError as e:
            logger.error(
                "HTTP请求错误：%s\n"
                "URL: %s\n"
                "Method: %s\n"
                "Params: %s\n"
                "Request-Headers: %s\n"
                "Request-Body: %s",
                str(e),
                url,
                method,
                _safe_dump(params),
                _safe_dump(_summarize_headers(request_headers)),
                _safe_dump(json_data),
                exc_info=True
            )
            return None
        except Exception as e:
            logger.error(
                "HTTP请求失败：%s\n"
                "URL: %s\n"
                "Method: %s\n"
                "Params: %s\n"
                "Request-Headers: %s\n"
                "Request-Body: %s",
                str(e),
                url,
                method,
                _safe_dump(params),
                _safe_dump(_summarize_headers(request_headers)),
                _safe_dump(json_data),
                exc_info=True
            )
            return None

    @classmethod
    async def _get_knowledge_networks(cls, headers: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """
        获取业务知识网络列表
        
        Args:
            headers: HTTP请求头
            
        Returns:
            知识网络列表
        """
        try:
            url = f"{KNOWLEDGE_NETWORK_API_BASE}/in/v1/knowledge-networks"
            params = {
                "include_detail": "false"
            }
            
            logger.debug(f"开始获取知识网络列表，URL: {url}")
            data = await cls._make_http_request(url, "GET", params=params, json_data=None, headers=headers)
            
            if data and "entries" in data:
                networks = data["entries"]
                logger.debug(f"成功获取知识网络列表，数量: {len(networks)}")
                return networks
            else:
                logger.warning("获取知识网络列表返回空数据")
                return []
                    
        except Exception as e:
            logger.error(f"获取知识网络列表失败: {str(e)}", exc_info=True)
            return []

    @classmethod
    async def _get_knowledge_network_detail(cls, kn_id: str, headers: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
        """
        获取知识网络详情
        
        Args:
            kn_id: 知识网络ID
            headers: HTTP请求头
            
        Returns:
            知识网络详情
        """
        try:
            url = f"{KNOWLEDGE_NETWORK_API_BASE}/in/v1/knowledge-networks/{kn_id}"
            params = {
                "include_detail": "true",
                "mode": "export"  # 新增mode=export参数
            }
            
            data = await cls._make_http_request(url, "GET", params=params, headers=headers)
            if data:
                logger.debug(f"成功获取知识网络详情 (ID: {kn_id})")
                return data
            else:
                logger.warning(f"获取知识网络详情返回空数据 (ID: {kn_id})")
                return None
                
        except Exception as e:
            logger.error(f"获取知识网络详情失败 (ID: {kn_id}): {str(e)}", exc_info=True)
            return None

    @classmethod
    async def coarse_recall_object_types(
        cls,
        kn_id: str,
        query: str,
        limit: int = 2000,
        headers: Optional[Dict[str, str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        对象类型粗召回（用于大规模知识网络下的候选裁剪）。

        NOTE: 请求体模板参考 docs/粗召回对象样例.txt，仅对 query 和 limit 做参数化。
        """
        url = f"{KNOWLEDGE_NETWORK_API_BASE}/in/v1/knowledge-networks/{kn_id}/object-types"
        body = {
            "condition": {
                "operation": "or",
                "sub_conditions": [
                    {
                        "field": "*",
                        "operation": "knn",
                        "sub_conditions": None,
                        "value": query,
                        "limit_key": "k",
                        "limit_value": str(limit),
                        "value_from": "const",
                    },
                    {
                        "field": "*",
                        "operation": "match",
                        "sub_conditions": None,
                        "value": query,
                        "value_from": "const",
                    },
                ],
            },
            "sort": [{"field": "_score", "direction": "desc"}],
            "limit": int(limit),
            "need_total": False,
        }
        request_headers: Dict[str, str] = {
            "X-HTTP-Method-Override": "GET",
            "Content-Type": "application/json",
        }
        if headers:
            # 允许调用方覆盖/补充账号相关头
            request_headers.update(headers)

        data = await cls._make_http_request(
            url,
            method="POST",
            json_data=body,
            headers=request_headers,
        )
        if isinstance(data, dict) and isinstance(data.get("entries"), list):
            return data["entries"]
        logger.warning("对象类型粗召回返回空或非法数据 (kn_id=%s)", kn_id)
        return []

    @classmethod
    async def coarse_recall_relation_types(
        cls,
        kn_id: str,
        query: str,
        limit: int = 300,
        headers: Optional[Dict[str, str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        关系类型粗召回（用于大规模知识网络下的候选裁剪）。

        NOTE: 请求体模板参考 docs/粗召回关系样例.txt，仅对 query 和 limit 做参数化。
        """
        url = f"{KNOWLEDGE_NETWORK_API_BASE}/in/v1/knowledge-networks/{kn_id}/relation-types"
        body = {
            "condition": {
                "operation": "or",
                "sub_conditions": [
                    {
                        "field": "*",
                        "operation": "match",
                        "sub_conditions": None,
                        "value": query,
                        "value_from": "const",
                    },
                    {
                        "field": "*",
                        "operation": "knn",
                        "sub_conditions": None,
                        "value": query,
                        "value_from": "const",
                        "limit_key": "k",
                        "limit_value": int(limit),
                    },
                ],
            },
            "sort": [{"field": "_score", "direction": "desc"}],
            "limit": int(limit),
            "need_total": False,
        }
        request_headers: Dict[str, str] = {
            "X-HTTP-Method-Override": "GET",
            "Content-Type": "application/json",
        }
        if headers:
            request_headers.update(headers)

        data = await cls._make_http_request(
            url,
            method="POST",
            json_data=body,
            headers=request_headers,
        )
        if isinstance(data, dict) and isinstance(data.get("entries"), list):
            return data["entries"]
        logger.warning("关系类型粗召回返回空或非法数据 (kn_id=%s)", kn_id)
        return []

    @classmethod
    async def query_object_instances(
        cls,
        kn_id: str,
        object_type_id: str,
        condition: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 5.0,
        ignoring_store_cache: bool = config.IGNORE_STORE_CACHE_DEFAULT
    ) -> Optional[Dict[str, Any]]:
        """统一的对象实例查询"""
        url = f"{config.KNOWLEDGE_NETWORK_QUERY_API_BASE}/knowledge-networks/{kn_id}/object-types/{object_type_id}"
        params = {"ignoring_store_cache": str(ignoring_store_cache).lower()} if ignoring_store_cache else None
        request_headers = {
            "X-HTTP-Method-Override": "GET",
            "Content-Type": "application/json"
        }
        if headers:
            request_headers.update(headers)
        return await cls._make_http_request(
            url,
            method="POST",
            params=params,
            json_data=condition,
            headers=request_headers,
            timeout=timeout
        )

    @classmethod
    async def query_relation_path(
        cls,
        kn_id: str,
        relation_type_paths: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 10.0,
        ignoring_store_cache: bool = config.IGNORE_STORE_CACHE_DEFAULT
    ) -> Optional[Dict[str, Any]]:
        """统一的关系路径查询"""
        url = f"{config.KNOWLEDGE_NETWORK_QUERY_API_BASE}/knowledge-networks/{kn_id}/subgraph"
        params = {"query_type": "relation_path"}
        if ignoring_store_cache:
            params["ignoring_store_cache"] = "true"
        request_headers = {
            "X-HTTP-Method-Override": "GET",
            "Content-Type": "application/json"
        }
        if headers:
            request_headers.update(headers)
        return await cls._make_http_request(
            url,
            method="POST",
            params=params,
            json_data=relation_type_paths,
            headers=request_headers,
            timeout=timeout
        )

    @classmethod
    async def query_relation_path_with_exception(
        cls,
        kn_id: str,
        relation_type_paths: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 30.0,
        ignoring_store_cache: bool = config.IGNORE_STORE_CACHE_DEFAULT
    ) -> Dict[str, Any]:
        """
        统一的关系路径查询（抛出异常版本）
        
        Args:
            kn_id: 知识网络ID
            relation_type_paths: 关系类型路径字典，格式: {"relation_type_paths": [...]}
            headers: HTTP请求头
            timeout: 请求超时时间，默认30.0秒
            ignoring_store_cache: 是否忽略存储缓存
            
        Returns:
            API返回结果
            
        Raises:
            HTTPException: 当API调用失败时，原样返回API的错误响应
        """
        url = f"{config.KNOWLEDGE_NETWORK_QUERY_API_BASE}/knowledge-networks/{kn_id}/subgraph"
        params = {"query_type": "relation_path"}
        if ignoring_store_cache:
            params["ignoring_store_cache"] = "true"
        
        request_headers = {
            "X-HTTP-Method-Override": "GET",
            "Content-Type": "application/json"
        }
        if headers:
            request_headers.update(headers)
        
        try:
            async with httpx.AsyncClient() as client:
                bucket = "path_query"
                parsed = urlparse(url)
                path_label = parsed.path or url
                query_type = (params or {}).get("query_type")
                label = f"POST {path_label}" + (f"?query_type={query_type}" if query_type else "")
                with api_timer(bucket, label=label):
                    response = await client.post(
                        url,
                        headers=request_headers,
                        params=params,
                        json=relation_type_paths,
                        timeout=timeout
                    )
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPStatusError as e:
            # API调用失败，原样返回API的错误响应
            status_code = e.response.status_code if e.response else 500
            error_detail = {}
            
            try:
                if e.response is not None:
                    # 尝试解析JSON响应
                    try:
                        error_detail = e.response.json()
                    except Exception:
                        # 如果不是JSON，返回文本
                        error_detail = {"error": e.response.text}
            except Exception:
                error_detail = {"error": str(e)}
            
            # 记录错误日志
            try:
                request_body_str = json.dumps(relation_type_paths, ensure_ascii=False, indent=2)
                logger.error(
                    f"调用关系路径检索API失败 (kn_id={kn_id}): HTTP {status_code}\n"
                    f"请求URL: {url}\n"
                    f"请求参数: {params}\n"
                    f"请求Body:\n{request_body_str}\n"
                    f"API错误响应: {json.dumps(error_detail, ensure_ascii=False, indent=2)}",
                    exc_info=True
                )
            except Exception as log_error:
                logger.error(
                    f"调用关系路径检索API失败 (kn_id={kn_id}): HTTP {status_code}\n"
                    f"打印请求Body时出错: {str(log_error)}",
                    exc_info=True
                )
            
            # 原样抛出API的错误响应
            raise HTTPException(status_code=status_code, detail=error_detail)
            
        except httpx.RequestError as e:
            # 网络请求错误
            error_detail = {"error": f"网络请求失败: {str(e)}"}
            logger.error(
                f"调用关系路径检索API网络请求失败 (kn_id={kn_id}): {str(e)}",
                exc_info=True
            )
            raise HTTPException(status_code=500, detail=error_detail)
            
        except Exception as e:
            # 其他未知错误
            error_detail = {"error": f"未知错误: {str(e)}"}
            try:
                request_body_str = json.dumps(relation_type_paths, ensure_ascii=False, indent=2)
                logger.error(
                    f"调用关系路径检索API失败 (kn_id={kn_id}): {str(e)}\n"
                    f"请求URL: {url}\n"
                    f"请求参数: {params}\n"
                    f"请求Body:\n{request_body_str}",
                    exc_info=True
                )
            except Exception as log_error:
                logger.error(
                    f"调用关系路径检索API失败 (kn_id={kn_id}): {str(e)}\n"
                    f"打印请求Body时出错: {str(log_error)}",
                    exc_info=True
                )
            raise HTTPException(status_code=500, detail=error_detail)