# -*- coding: utf-8 -*-
"""
根据关系路径检索对象工具（带属性过滤）
基于关系路径检索接口，根据properties字段过滤结果，返回SQL格式的数据
"""

import json
from typing import List, Dict, Any, Optional, Set, Tuple
from fastapi import Body, HTTPException, Header, Depends
from pydantic import BaseModel, Field, ConfigDict

# 导入日志模块
from data_retrieval.logs.logger import logger
# 导入标准错误响应类
from data_retrieval.errors import KnowledgeNetworkRetrievalError, KnowledgeNetworkParamError
# 导入配置
from ..config import config
# 导入HeaderParams
from ..models import HeaderParams
# 导入HTTP客户端
from ..infra.clients.http_client import KnowledgeNetworkHTTPClient


class SingleCondition(BaseModel):
    """单个条件配置"""
    field: str = Field(description="字段名")
    operation: str = Field(description="比较操作符，如 '==', '>', '<', '>=' 等")
    value: Any = Field(description="字段值")
    value_from: Optional[str] = Field(default="const", description="值来源，如 'const'")


class ConditionConfig(BaseModel):
    """条件组配置（顶层条件）
    
    顶层条件组只包含 operation 和 sub_conditions 两个字段。
    sub_conditions 是单个条件的数组，不支持嵌套。
    """
    operation: str = Field(description="逻辑操作符，如 'and', 'or'")
    sub_conditions: List[SingleCondition] = Field(description="子条件列表，每个子条件是单个条件（包含 field, operation, value, value_from），不支持嵌套")
    
    model_config = ConfigDict(extra="forbid")  # 禁止额外字段，确保只有 operation 和 sub_conditions


class ObjectTypeConfig(BaseModel):
    """对象类型配置"""
    id: str = Field(description="对象类型ID")
    condition: Optional[Any] = Field(default=None, description="查询条件，统一使用sub_conditions结构。格式：{operation: 'and', sub_conditions: [{field: '...', operation: '==', value: '...', value_from: 'const'}]}。支持ConditionConfig对象或字典格式（字典格式可用于KNN等需要额外参数的操作符）")
    limit: Optional[int] = Field(default=50, description="返回结果数量限制（默认值50，最大不超过100，用于控制token消耗）")
    properties: Optional[List[str]] = Field(default=None, description="需要返回的属性列表，只有指定了properties的对象才会在结果中保留")


class RelationTypeConfig(BaseModel):
    """关系类型配置"""
    relation_type_id: str = Field(description="关系类型ID")
    source_object_type_id: str = Field(description="源对象类型ID")
    target_object_type_id: str = Field(description="目标对象类型ID")


class RelationTypePathConfig(BaseModel):
    """关系类型路径配置"""
    object_types: List[ObjectTypeConfig] = Field(description="对象类型列表")
    relation_types: List[RelationTypeConfig] = Field(description="关系类型列表")
    limit: Optional[int] = Field(default=50, description="路径数量限制（默认值50，最大不超过100，用于控制token消耗）")


class RelationPathRetrievalInput(BaseModel):
    """关系路径检索输入参数"""
    kn_id: str = Field(description="知识网络ID")
    relation_type_paths: List[RelationTypePathConfig] = Field(description="关系类型路径列表")


class RelationPathRetrievalTool:
    """根据关系路径检索对象工具（带属性过滤）"""
    # 后端上限（用户给定）：limit 最大限制，防止token消耗过大（降低到100以控制上下文长度）
    MAX_REQUEST_LIMIT: int = 100
    # 工具默认：未传 limit 时使用该默认值，降低默认值以控制token消耗
    DEFAULT_LIMIT: int = 50
    # 工具最终返回上限：与MAX_REQUEST_LIMIT保持一致，避免返回过大导致调用方/网络/内存压力
    MAX_RETURN_ROWS: int = 100
    # 每个分组（每个 entry/path）最大参与汇总的行数（用于均衡多路径场景，避免单一路径占满全局行数）
    MAX_GROUP_RETURN_ROWS: int = 1000
    
    def __init__(self):
        pass
    
    @classmethod
    async def _call_relation_path_api(
        cls,
        kn_id: str,
        relation_type_paths: List[Dict[str, Any]],
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        调用关系路径检索API
        
        Args:
            kn_id: 知识网络ID
            relation_type_paths: 关系类型路径列表
            headers: HTTP请求头
            
        Returns:
            API返回结果
            
        Raises:
            HTTPException: 当API调用失败时，原样返回API的错误响应
        """
        # 构建请求体
        request_body = {
            "relation_type_paths": relation_type_paths
        }
        
        # 使用HTTP客户端的方法
        return await KnowledgeNetworkHTTPClient.query_relation_path_with_exception(
            kn_id=kn_id,
            relation_type_paths=request_body,
            headers=headers,
            timeout=30.0
        )
    
    @classmethod
    def _extract_properties_from_request(
        cls,
        relation_type_paths: List[Dict[str, Any]]
    ) -> Dict[str, List[str]]:
        """
        从请求中提取每个对象类型需要返回的属性列表
        
        Args:
            relation_type_paths: 关系类型路径列表
            
        Returns:
            对象类型ID到属性列表的映射，格式: {object_type_id: [property1, property2, ...]}
        """
        properties_map = {}
        
        for path in relation_type_paths:
            object_types = path.get("object_types", [])
            for obj_type in object_types:
                object_type_id = obj_type.get("id")
                # 使用properties字段名（与ObjectTypeConfig模型定义一致）
                properties = obj_type.get("properties")
                
                if object_type_id and properties and isinstance(properties, list):
                    # 如果该对象类型已经有properties，合并（去重）
                    if object_type_id in properties_map:
                        existing_props = set(properties_map[object_type_id])
                        new_props = set(properties)
                        properties_map[object_type_id] = list(existing_props | new_props)
                    else:
                        properties_map[object_type_id] = properties
        
        return properties_map

    @classmethod
    def _extract_properties_filter_map_from_models(
        cls,
        relation_type_paths: List["RelationTypePathConfig"],
    ) -> Dict[str, Set[str]]:
        """
        从请求模型中提取属性过滤映射（用于过滤结果）。

        Returns:
            {object_type_id: {prop1, prop2, ...}}
        """
        out: Dict[str, Set[str]] = {}
        for path in relation_type_paths:
            for obj in path.object_types:
                if not obj.id or not obj.properties:
                    continue
                out.setdefault(obj.id, set()).update([p for p in obj.properties if isinstance(p, str) and p])
        return out

    @classmethod
    def _extract_requested_columns_by_path_from_models(
        cls,
        relation_type_paths: List["RelationTypePathConfig"],
    ) -> Tuple[List[str], List[List[str]]]:
        """
        按请求顺序提取“类SQL列名”（object_type.property），并按 relation_type_paths 分组。

        Returns:
            - overall_columns: 全局列（按请求出现顺序去重）
            - columns_by_path: 每条路径的列（按该路径的 object_types 顺序与 properties 顺序）
        """
        overall_columns: List[str] = []
        overall_seen: Set[str] = set()
        columns_by_path: List[List[str]] = []

        for path in relation_type_paths:
            cols: List[str] = []
            seen: Set[str] = set()
            for obj in path.object_types:
                if not obj.id or not obj.properties:
                    continue
                for prop in obj.properties:
                    if not isinstance(prop, str) or not prop:
                        continue
                    col = f"{obj.id}.{prop}"
                    if col not in seen:
                        cols.append(col)
                        seen.add(col)
                    if col not in overall_seen:
                        overall_columns.append(col)
                        overall_seen.add(col)
            columns_by_path.append(cols)

        return overall_columns, columns_by_path
    
    @classmethod
    def _filter_and_transform_results(
        cls,
        api_result: Dict[str, Any],
        properties_map: Dict[str, List[str]]
    ) -> List[Dict[str, Any]]:
        """
        过滤和转换API返回结果，只保留有properties字段的对象和属性，转换为SQL格式
        
        Args:
            api_result: API返回的原始结果
            properties_map: 对象类型ID到属性列表的映射
            
        Returns:
            转换后的结果列表，格式: [{"object_type.property": value, ...}, ...]
        """
        results = []
        
        # 如果没有指定任何properties，返回空列表
        if not properties_map:
            logger.warning("没有指定任何properties，返回空结果")
            return results
        
        entries = api_result.get("entries", [])
        if not entries:
            logger.warning("API返回结果中没有entries")
            return results
        
        # 遍历每个entry
        for entry in entries:
            objects = entry.get("objects", {})
            relation_paths = entry.get("relation_paths", [])
            
            # 如果没有relation_paths，跳过
            if not relation_paths:
                continue
            
            # 遍历每个relation_path，每个path对应一行结果
            for relation_path in relation_paths:
                relations = relation_path.get("relations", [])
                if not relations:
                    continue
                
                # 构建该路径对应的结果行
                result_row = {}
                
                # 遍历该路径中的所有关系，收集涉及的对象
                involved_object_ids = set()
                for relation in relations:
                    source_object_id = relation.get("source_object_id")
                    target_object_id = relation.get("target_object_id")
                    if source_object_id:
                        involved_object_ids.add(source_object_id)
                    if target_object_id:
                        involved_object_ids.add(target_object_id)
                
                # 遍历涉及的对象，提取需要的属性
                for object_id in involved_object_ids:
                    obj = objects.get(object_id)
                    if not obj:
                        continue
                    
                    object_type_id = obj.get("object_type_id")
                    if not object_type_id:
                        continue
                    
                    # 检查该对象类型是否在properties_map中
                    if object_type_id not in properties_map:
                        # 该对象类型没有指定properties，跳过
                        continue
                    
                    # 获取该对象类型需要返回的属性列表
                    required_properties = properties_map[object_type_id]
                    if not required_properties:
                        continue
                    
                    # 获取对象的properties
                    obj_properties = obj.get("properties", {})
                    if not isinstance(obj_properties, dict):
                        continue
                    
                    # 提取需要的属性
                    for prop_name in required_properties:
                        if prop_name in obj_properties:
                            # 构建SQL格式的key: object_type_id.property_name
                            key = f"{object_type_id}.{prop_name}"
                            value = obj_properties[prop_name]
                            result_row[key] = value
                
                # 只有当result_row不为空时才添加到结果中
                if result_row:
                    results.append(result_row)
        
        return results

    @classmethod
    def _filter_and_transform_results_grouped(
        cls,
        api_result: Dict[str, Any],
        properties_filter_map: Dict[str, Set[str]],
    ) -> Tuple[List[Dict[str, Any]], List[List[Dict[str, Any]]]]:
        """
        将底层 API 返回转为“行字典”，并按 entries 分组。

        Returns:
            - overall_rows: 全量行（每行对应一个 relation_path）
            - rows_by_entry: 按 entry 分组的行
        """
        overall_rows: List[Dict[str, Any]] = []
        rows_by_entry: List[List[Dict[str, Any]]] = []

        if not properties_filter_map:
            logger.warning("没有指定任何properties，返回空结果")
            return overall_rows, rows_by_entry

        entries = api_result.get("entries", [])
        if not entries:
            logger.warning("API返回结果中没有entries")
            return overall_rows, rows_by_entry

        for entry in entries:
            entry_rows: List[Dict[str, Any]] = []
            objects = entry.get("objects", {})
            relation_paths = entry.get("relation_paths", [])
            if not relation_paths:
                rows_by_entry.append(entry_rows)
                continue

            for relation_path in relation_paths:
                relations = relation_path.get("relations", [])
                if not relations:
                    continue

                involved_object_ids: Set[str] = set()
                for relation in relations:
                    source_object_id = relation.get("source_object_id")
                    target_object_id = relation.get("target_object_id")
                    if source_object_id:
                        involved_object_ids.add(source_object_id)
                    if target_object_id:
                        involved_object_ids.add(target_object_id)

                row: Dict[str, Any] = {}
                for object_id in involved_object_ids:
                    obj = objects.get(object_id)
                    if not obj:
                        continue
                    object_type_id = obj.get("object_type_id")
                    if not object_type_id or object_type_id not in properties_filter_map:
                        continue
                    obj_properties = obj.get("properties", {})
                    if not isinstance(obj_properties, dict):
                        continue
                    for prop_name in properties_filter_map[object_type_id]:
                        if prop_name in obj_properties:
                            row[f"{object_type_id}.{prop_name}"] = obj_properties[prop_name]

                if row:
                    entry_rows.append(row)
                    overall_rows.append(row)

            rows_by_entry.append(entry_rows)

        return overall_rows, rows_by_entry

    @classmethod
    def _rows_to_table(cls, columns: List[str], rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        将行字典转换为类 SQL 的 table 结构：
        - columns: 列名数组
        - rows: 二维数组，按 columns 对齐，缺失为 null
        """
        return {
            "columns": columns,
            "rows": [[r.get(c) for c in columns] for r in rows],
        }
    
    @classmethod
    async def retrieve(
        cls,
        kn_id: str,
        relation_type_paths: List["RelationTypePathConfig"],
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        执行关系路径检索并过滤属性（精简返回：meta + table）
        
        Args:
            kn_id: 知识网络ID
            relation_type_paths: 关系类型路径列表（Pydantic模型）
            headers: HTTP请求头
            
        Returns:
            新返回结构（不兼容旧版）:
            {
              "meta": {...},
              "table": {"columns": [...], "rows": [[...], ...]}
            }
        """
        default_limit = int(cls.DEFAULT_LIMIT)

        overall_columns, columns_by_path = cls._extract_requested_columns_by_path_from_models(relation_type_paths)
        properties_filter_map = cls._extract_properties_filter_map_from_models(relation_type_paths)

        # 没有任何 properties：直接返回空 table，并在 meta 里明确说明（避免误解为"只查到 0 条"）
        if not properties_filter_map or not overall_columns:
            logger.warning("请求中没有指定任何properties字段，返回空结果")
            # 计算默认的requested_limit（取路径limit的最大值，但不超过MAX_REQUEST_LIMIT）
            max_path_limit = max(
                (path.limit if path.limit is not None else default_limit for path in relation_type_paths),
                default=default_limit
            )
            actual_requested_limit = min(max_path_limit, cls.MAX_REQUEST_LIMIT)
            
            meta = {
                "row_count": 0,
                "requested_limit": actual_requested_limit,
                "limit_status": "未限制"
            }
            return {
                "meta": meta,
                "table": {"columns": overall_columns, "rows": []},
            }

        # 将Pydantic模型转换为底层API所需字典，同时跟踪limit限制信息
        relation_type_paths_dict: List[Dict[str, Any]] = []
        limit_limited = False  # 是否有任何limit被限制
        max_requested_limit = None  # 记录最大的请求limit值
        
        for path in relation_type_paths:
            # 对后端请求做上限保护（<= MAX_REQUEST_LIMIT）；未传时使用 DEFAULT_LIMIT（已由 Pydantic 默认给到）
            requested_path_limit = path.limit if path.limit is not None else default_limit
            if max_requested_limit is None or requested_path_limit > max_requested_limit:
                max_requested_limit = requested_path_limit
            
            safe_path_limit = min(int(requested_path_limit), int(cls.MAX_REQUEST_LIMIT))
            if requested_path_limit > cls.MAX_REQUEST_LIMIT:
                limit_limited = True
                logger.warning(
                    f"关系路径检索path limit={requested_path_limit}超过上限{cls.MAX_REQUEST_LIMIT}，已限制为{cls.MAX_REQUEST_LIMIT}"
                )
            
            relation_type_paths_dict.append(
                {
                    "object_types": [
                        {
                            # 处理condition字段：如果是字典则直接使用，如果是ConditionConfig对象则转换；
                            # 其余字段中显式排除 limit，避免在对象级别向底层API传递limit，
                            # 只在路径级别使用 RelationTypePathConfig.limit 控制整体数量。
                            **({
                                "condition": obj.condition if isinstance(obj.condition, dict) 
                                            else obj.condition.model_dump(exclude_none=True) if obj.condition is not None 
                                            else None,
                                **{k: v for k, v in obj.model_dump(exclude_none=True).items() if k not in ("condition", "limit")}
                            } if obj.condition is not None else {k: v for k, v in obj.model_dump(exclude_none=True).items() if k != "condition" and k != "limit"}),
                        }
                        for obj in path.object_types
                    ],
                    "relation_types": [rel.model_dump(exclude_none=True) for rel in path.relation_types],
                    "limit": safe_path_limit,
                }
            )

        api_result = await cls._call_relation_path_api(kn_id, relation_type_paths_dict, headers)

        overall_rows, rows_by_entry = cls._filter_and_transform_results_grouped(api_result, properties_filter_map)

        # 先做"分组内截断"，再合并做全局截断：保证多条路径时不会被某一条路径的海量结果占满。
        merged_rows: List[Dict[str, Any]] = []
        for entry_rows in rows_by_entry:
            merged_rows.extend(entry_rows[: int(cls.MAX_GROUP_RETURN_ROWS)])

        # 全局截断：限制在MAX_RETURN_ROWS内（与MAX_REQUEST_LIMIT保持一致）
        safe_overall_rows = merged_rows[: int(cls.MAX_RETURN_ROWS)]
        
        # 关系路径检索的meta：统一返回row_count、requested_limit和limit_status（便于大模型理解）
        # 注意：已去掉truncated字段，因为MAX_RETURN_ROWS与MAX_REQUEST_LIMIT一致，不会触发截断
        # 计算实际查询使用的limit值（取路径limit和对象limit的最大值，但不超过MAX_REQUEST_LIMIT）
        actual_requested_limit = min(
            max_requested_limit if max_requested_limit is not None else default_limit,
            cls.MAX_REQUEST_LIMIT
        )
        
        limit_status = (
            f"查询数量已限制到上限{cls.MAX_REQUEST_LIMIT}" 
            if limit_limited 
            else "未限制"
        )
        meta = {
            "row_count": len(safe_overall_rows),  # 实际返回的行数
            "requested_limit": actual_requested_limit,  # 实际查询使用的limit值
            "limit_status": limit_status  # 限制状态（文本描述，便于大模型理解）
        }
        
        if len(merged_rows) > len(safe_overall_rows):
            logger.warning(
                f"关系路径检索结果过大，已截断：before={len(merged_rows)} after={len(safe_overall_rows)} max_return_rows={cls.MAX_RETURN_ROWS}"
            )
        logger.info(f"关系路径检索完成，返回 {len(safe_overall_rows)} 行（精简table输出）")

        return {
            "meta": meta,
            "table": cls._rows_to_table(overall_columns, safe_overall_rows),
        }
    
    @classmethod
    async def as_async_api_cls(cls, params: dict = Body(...), header_params: HeaderParams = Depends()):
        """
        API接口方法
        
        Args:
            params: API请求参数
            header_params: 请求头参数对象
            
        Returns:
            检索结果
        """
        try:
            # 参数验证阶段
            try:
                # 验证参数
                input_data = RelationPathRetrievalInput(**params)
                logger.debug(f"参数验证通过: {input_data}")
                
                # 构建headers字典
                headers_dict = {
                    "x-account-type": header_params.account_type,
                    "x-account-id": header_params.account_id,
                    "Content-Type": header_params.content_type
                }
                logger.debug("请求头构建完成")
            except Exception as e:
                logger.error(f"参数验证失败: {str(e)}")
                raise KnowledgeNetworkParamError(
                    detail={"error": str(e)},
                    link="https://example.com/api-docs/relation-path-retrieval"
                )
            
            # 执行检索（如果API调用失败，_call_relation_path_api会抛出HTTPException，包含API的原始错误响应）
            result = await cls.retrieve(
                kn_id=input_data.kn_id,
                relation_type_paths=input_data.relation_type_paths,
                headers=headers_dict
            )
            
            logger.debug("关系路径检索执行完成")
            return result
        except HTTPException:
            # 重新抛出 HTTPException，保持原有行为
            raise
        except (KnowledgeNetworkRetrievalError, KnowledgeNetworkParamError) as e:
            # 将自定义异常转换为标准化错误响应
            raise HTTPException(
                status_code=400 if isinstance(e, KnowledgeNetworkParamError) else 500,
                detail=e.json()
            )
    
    @classmethod
    async def get_api_schema(cls):
        """获取API schema定义"""
        return {
            "post": {
                "summary": "kn_path_search",
                "description": "根据关系路径检索对象，并根据properties字段过滤结果。返回结构为 meta + table（类SQL：columns + rows），面向大模型问答场景做了精简。注意：该返回格式为新版本，不兼容旧版 results 平铺结构。",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "kn_id": {
                                        "type": "string",
                                        "description": "知识网络ID"
                                    },
                                    "relation_type_paths": {
                                        "type": "array",
                                        "description": "关系类型路径列表",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "object_types": {
                                                    "type": "array",
                                                    "description": "对象类型列表",
                                                    "items": {
                                                        "type": "object",
                                                        "properties": {
                                                            "id": {
                                                                "type": "string",
                                                                "description": "对象类型ID"
                                                            },
                                                            "condition": {
                                                                "type": "object",
                                                                "description": "查询条件，统一使用sub_conditions结构。顶层只有operation和sub_conditions两个字段。单个条件：{operation: 'and', sub_conditions: [{field: 'name', operation: '==', value: '张三', value_from: 'const'}]}。多个条件：{operation: 'and', sub_conditions: [{field: 'p_gender', operation: '==', value: 'male', value_from: 'const'}, {field: 'age', operation: '>', value: 30, value_from: 'const'}]}",
                                                                "nullable": True,
                                                                "properties": {
                                                                    "operation": {
                                                                        "type": "string",
                                                                        "description": "逻辑操作符，如 'and', 'or'",
                                                                        "enum": ["and", "or"]
                                                                    },
                                                                    "sub_conditions": {
                                                                        "type": "array",
                                                                        "description": "子条件列表，不支持嵌套。每个子条件是单个条件，包含 field, operation（比较操作符）, value, value_from",
                                                                        "items": {
                                                                            "type": "object",
                                                                            "properties": {
                                                                                "field": {
                                                                                    "type": "string",
                                                                                    "description": "字段名"
                                                                                },
                                                                                "operation": {
                                                                                    "type": "string",
                                                                                    "description": "比较操作符，如 '==', '>', '<', '>=', '<=' 等"
                                                                                },
                                                                                "value": {
                                                                                    "description": "字段值"
                                                                                },
                                                                                "value_from": {
                                                                                    "type": "string",
                                                                                    "description": "值来源，如 'const'",
                                                                                    "default": "const"
                                                                                }
                                                                            },
                                                                            "required": ["field", "operation", "value"]
                                                                        }
                                                                    }
                                                                },
                                                                "required": ["operation", "sub_conditions"]
                                                            },
                                                            "limit": {
                                                                "type": "integer",
                                                                "description": "返回结果数量限制",
                                                                "default": 10,
                                                                "nullable": True
                                                            },
                                                            "properties": {
                                                                "type": "array",
                                                                "description": "需要返回的属性列表，只有指定了properties的对象才会在结果中保留",
                                                                "items": {
                                                                    "type": "string"
                                                                },
                                                                "nullable": True
                                                            }
                                                        },
                                                        "required": ["id"]
                                                    }
                                                },
                                                "relation_types": {
                                                    "type": "array",
                                                    "description": "关系类型列表",
                                                    "items": {
                                                        "type": "object",
                                                        "properties": {
                                                            "relation_type_id": {
                                                                "type": "string",
                                                                "description": "关系类型ID"
                                                            },
                                                            "source_object_type_id": {
                                                                "type": "string",
                                                                "description": "源对象类型ID"
                                                            },
                                                            "target_object_type_id": {
                                                                "type": "string",
                                                                "description": "目标对象类型ID"
                                                            }
                                                        },
                                                        "required": ["relation_type_id", "source_object_type_id", "target_object_type_id"]
                                                    }
                                                },
                                                "limit": {
                                                    "type": "integer",
                                                    "description": "路径数量限制",
                                                    "default": 10,
                                                    "nullable": True
                                                }
                                            },
                                            "required": ["object_types", "relation_types"]
                                        }
                                    }
                                },
                                "required": ["kn_id", "relation_type_paths"]
                            },
                            "examples": {
                                "basic_query": {
                                    "summary": "基本查询示例",
                                    "description": "查询上气道梗阻的症状，只返回symptom对象的symptom_name属性",
                                    "value": {
                                        "kn_id": "kn_medical",
                                        "relation_type_paths": [
                                            {
                                                "object_types": [
                                                    {
                                                        "id": "disease",
                                                        "condition": {
                                                            "operation": "and",
                                                            "sub_conditions": [
                                                                {
                                                                    "field": "disease_name",
                                                                    "operation": "==",
                                                                    "value": "上气道梗阻",
                                                                    "value_from": "const"
                                                                }
                                                            ]
                                                        },
                                                        "limit": 10,
                                                        "properties": ["disease_name"]
                                                    },
                                                    {
                                                        "id": "symptom",
                                                        "limit": 10,
                                                        "properties": ["symptom_name"]
                                                    }
                                                ],
                                                "relation_types": [
                                                    {
                                                        "relation_type_id": "has_symptom",
                                                        "source_object_type_id": "disease",
                                                        "target_object_type_id": "symptom"
                                                    }
                                                ],
                                                "limit": 10
                                            }
                                        ]
                                    }
                                }
                            }
                        }
                    }
                },
                "parameters": [
                    {
                        "name": "x-account-id",
                        "in": "header",
                        "required": False,
                        "schema": {
                            "type": "string"
                        },
                        "description": "账户ID，用于内部服务调用时传递账户信息"
                    },
                    {
                        "name": "x-account-type",
                        "in": "header",
                        "required": False,
                        "schema": {
                            "type": "string",
                            "enum": ["user", "app", "anonymous"],
                            "default": "user"
                        },
                        "description": "账户类型：user(用户), app(应用), anonymous(匿名)"
                    },
                    {
                        "name": "Content-Type",
                        "in": "header",
                        "required": False,
                        "schema": {
                            "type": "string",
                            "default": "application/json"
                        },
                        "description": "内容类型"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Successful operation",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "description": "检索结果（meta + table）",
                                    "properties": {
                                        "meta": {
                                            "type": "object",
                                            "description": "请求与执行元信息（包含默认limit是否生效、最终生效limit、行数等）"
                                        },
                                        "table": {
                                            "type": "object",
                                            "description": "全局结果表（类SQL）",
                                            "properties": {
                                                "columns": {"type": "array", "items": {"type": "string"}},
                                                "rows": {
                                                    "type": "array",
                                                    "items": {"type": "array", "items": {}}
                                                }
                                            },
                                            "required": ["columns", "rows"]
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

