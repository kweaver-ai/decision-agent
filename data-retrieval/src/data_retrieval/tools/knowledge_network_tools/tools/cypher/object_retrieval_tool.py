# -*- coding: utf-8 -*-
"""
单个对象检索工具
封装对象检索API调用和结果处理
"""

from typing import Dict, Any, Optional

from data_retrieval.logs.logger import logger
from data_retrieval.errors import KnowledgeNetworkRetrievalError

from ...infra.clients.http_client import KnowledgeNetworkHTTPClient


class ObjectRetrievalTool:
    """单个对象检索工具"""
    
    # 默认limit：未指定时使用，降低默认值以控制token消耗
    DEFAULT_LIMIT: int = 50
    # API请求上限：防止用户指定过大limit导致token消耗过大（降低到100以控制上下文长度）
    MAX_REQUEST_LIMIT: int = 100
    
    @classmethod
    async def retrieve(
        cls,
        kn_id: str,
        object_type_id: str,
        condition: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        properties: Optional[list] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        执行单个对象检索
        
        Args:
            kn_id: 知识网络ID
            object_type_id: 对象类型ID
            condition: 查询条件
            limit: 结果数量限制（可选，未指定时使用DEFAULT_LIMIT=50，最大不超过MAX_REQUEST_LIMIT=100）
            properties: 需要返回的属性列表（可选），如果指定则只返回这些属性
            headers: HTTP请求头
            
        Returns:
            检索结果，格式：
            {
                "meta": {
                    "kn_id": ...,
                    "object_type_id": ...,
                    "row_count": ...,
                    ...
                },
                "table": {
                    "columns": [...],
                    "rows": [[...], ...]
                }
            }
        """
        # 确定实际使用的limit值：未指定时使用默认值，并限制在最大上限内
        requested_limit = limit  # 保存原始请求值用于日志
        effective_limit = limit if limit is not None else cls.DEFAULT_LIMIT
        limit_limited = False
        if effective_limit > cls.MAX_REQUEST_LIMIT:
            limit_limited = True
            effective_limit = cls.MAX_REQUEST_LIMIT
            logger.warning(
                f"对象检索limit={requested_limit}超过上限{cls.MAX_REQUEST_LIMIT}，已限制为{cls.MAX_REQUEST_LIMIT}"
            )
        
        # 构建请求参数
        request_params = {
            "limit": effective_limit
        }
        
        if condition:
            request_params["condition"] = condition
        
        # 如果指定了properties，添加到请求参数中
        if properties and isinstance(properties, list) and len(properties) > 0:
            request_params["properties"] = properties
        
        try:
            # 调用API
            api_result = await KnowledgeNetworkHTTPClient.query_object_instances(
                kn_id=kn_id,
                object_type_id=object_type_id,
                condition=request_params,
                headers=headers,
                timeout=30.0
            )
            
            if not api_result:
                logger.warning(f"对象检索API返回空结果 (kn_id={kn_id}, object_type_id={object_type_id})")
                return cls._build_empty_result(kn_id, object_type_id, effective_limit)
            
            # 转换结果格式
            return cls._transform_result(
                api_result, kn_id, object_type_id, properties, 
                limit_limited=limit_limited,
                requested_limit=effective_limit  # 实际查询使用的limit值
            )
            
        except Exception as e:
            logger.error(f"对象检索失败: {str(e)}", exc_info=True)
            raise KnowledgeNetworkRetrievalError(
                detail={
                    "error": f"对象检索失败: {str(e)}",
                    "kn_id": kn_id,
                    "object_type_id": object_type_id
                }
            )
    
    @classmethod
    def _transform_result(
        cls,
        api_result: Dict[str, Any],
        kn_id: str,
        object_type_id: str,
        requested_properties: Optional[list] = None,
        limit_limited: bool = False,
        requested_limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        转换API结果为统一格式（table格式）
        
        Args:
            api_result: API返回的原始结果
            kn_id: 知识网络ID
            object_type_id: 对象类型ID
            requested_properties: 请求的属性列表（可选），如果指定则只返回这些属性并保持顺序
            
        Returns:
            转换后的结果
        """
        datas = api_result.get("datas", [])
        
        if not datas:
            return cls._build_empty_result(kn_id, object_type_id)
        
        # 确定要返回的列
        if requested_properties and isinstance(requested_properties, list) and len(requested_properties) > 0:
            # 如果指定了properties，只返回这些属性，并保持顺序
            columns = [f"{object_type_id}.{prop}" for prop in requested_properties]
        else:
            # 如果没有指定，返回所有字段（从第一条数据中获取）
            if datas:
                columns = [f"{object_type_id}.{col}" for col in datas[0].keys()]
            else:
                columns = []
        
        # 构建行数据
        rows = []
        for data in datas:
            row = []
            for col in columns:
                # 从列名中提取字段名（去掉 object_type. 前缀）
                field_name = col.replace(f"{object_type_id}.", "")
                row.append(data.get(field_name))
            rows.append(row)
        
        # 构建meta信息：统一返回row_count、requested_limit和limit_status（便于大模型理解）
        limit_status = (
            f"查询数量已限制到上限{cls.MAX_REQUEST_LIMIT}" 
            if limit_limited 
            else "未限制"
        )
        meta = {
            "row_count": len(rows),  # 实际返回的行数
            "requested_limit": requested_limit if requested_limit is not None else cls.DEFAULT_LIMIT,  # 实际查询使用的limit值
            "limit_status": limit_status  # 限制状态（文本描述，便于大模型理解）
        }
        
        return {
            "meta": meta,
            "table": {
                "columns": columns,
                "rows": rows
            }
        }
    
    @classmethod
    def _build_empty_result(cls, kn_id: str, object_type_id: str, requested_limit: Optional[int] = None) -> Dict[str, Any]:
        """构建空结果"""
        return {
            "meta": {
                "row_count": 0,
                "requested_limit": requested_limit if requested_limit is not None else cls.DEFAULT_LIMIT,
                "limit_status": "未限制"
            },
            "table": {
                "columns": [],
                "rows": []
            }
        }

