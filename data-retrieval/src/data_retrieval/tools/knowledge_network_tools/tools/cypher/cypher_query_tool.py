# -*- coding: utf-8 -*-
"""
Cypher查询工具
主工具类，整合Cypher解析、转换和检索功能
"""

import json
from typing import Dict, Any, Optional

from fastapi import Body, HTTPException, Header, Depends
from pydantic import BaseModel, Field

from data_retrieval.logs.logger import logger
from data_retrieval.errors import KnowledgeNetworkParamError, KnowledgeNetworkRetrievalError

from ...models import HeaderParams
from .parser import CypherParser
from .converter import CypherConverter
from .templates import QueryType
from .object_retrieval_tool import ObjectRetrievalTool
from ..relation_path_retrieval_tool import RelationPathRetrievalTool


class CypherQueryInput(BaseModel):
    """Cypher查询输入参数"""
    kn_id: str = Field(description="知识网络ID")
    cypher: str = Field(description="Cypher查询语句，支持单个对象检索和关系路径查询（2-4节点）")


class CypherQueryTool:
    """Cypher查询工具"""
    
    @classmethod
    async def query(
        cls,
        kn_id: str,
        cypher: str,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        执行Cypher查询
        
        Args:
            kn_id: 知识网络ID
            cypher: Cypher查询语句
            headers: HTTP请求头
            
        Returns:
            检索结果（meta + table格式）
        """
        try:
            # 1. 解析Cypher
            parsed = CypherParser.parse(cypher)
            logger.debug(f"Cypher解析成功，查询类型: {parsed.query_type.value}")
            
            # 2. 根据查询类型执行不同的检索
            if parsed.query_type == QueryType.SINGLE_OBJECT:
                # 单个对象检索
                params = CypherConverter.convert_to_object_retrieval_params(kn_id, parsed)
                logger.debug(f"转换为对象检索参数: object_type_id={params['object_type_id']}")
                # 打印最终调用知识网络对象检索接口的请求体，便于排查转换结果
                object_request_body = {
                    "kn_id": params.get("kn_id"),
                    "object_type_id": params.get("object_type_id"),
                    "request_body": {
                        k: v for k, v in {
                            "limit": params.get("limit"),
                            "condition": params.get("condition"),
                            "properties": params.get("properties")
                        }.items() if v is not None
                    }
                }
                logger.debug(
                    "对象检索API请求体:\n%s",
                    json.dumps(object_request_body, ensure_ascii=False, indent=2)
                )
                
                result = await ObjectRetrievalTool.retrieve(
                    kn_id=params["kn_id"],
                    object_type_id=params["object_type_id"],
                    condition=params.get("condition"),
                    limit=params.get("limit"),  # 传入None时使用工具默认值
                    properties=params.get("properties"),
                    headers=headers
                )
                
            elif parsed.query_type == QueryType.RELATION_PATH:
                # 关系路径检索
                input_data = CypherConverter.convert_to_relation_path_params(kn_id, parsed)
                logger.debug(f"转换为关系路径检索参数，路径数: {len(input_data.relation_type_paths)}")
                # 打印最终调用知识网络关系路径检索接口的请求体
                relation_request_body = input_data.model_dump(exclude_none=True)
                logger.debug(
                    "关系路径检索API请求体:\n%s",
                    json.dumps(relation_request_body, ensure_ascii=False, indent=2)
                )
                
                result = await RelationPathRetrievalTool.retrieve(
                    kn_id=input_data.kn_id,
                    relation_type_paths=input_data.relation_type_paths,
                    headers=headers
                )
                
            else:
                raise ValueError(f"不支持的查询类型: {parsed.query_type}")
            
            logger.debug("Cypher查询执行完成")
            return result
            
        except KnowledgeNetworkParamError:
            raise
        except KnowledgeNetworkRetrievalError:
            raise
        except Exception as e:
            logger.error(f"Cypher查询失败: {str(e)}", exc_info=True)
            raise KnowledgeNetworkParamError(
                detail={
                    "error": f"Cypher查询执行失败: {str(e)}",
                    "hint": "请检查Cypher语法是否正确，是否符合支持的模板"
                }
            )
    
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
            # 参数验证
            try:
                input_data = CypherQueryInput(**params)
                logger.debug(f"Cypher查询输入: {input_data.cypher[:100]}...")
            except Exception as e:
                logger.error(f"参数验证失败: {str(e)}")
                raise KnowledgeNetworkParamError(
                    detail={"error": str(e)},
                    link="https://example.com/api-docs/cypher-query"
                )
            
            # 构建headers
            headers_dict = {
                "x-account-type": header_params.account_type,
                "x-account-id": header_params.account_id,
                "Content-Type": header_params.content_type
            }
            
            # 执行查询
            result = await cls.query(
                kn_id=input_data.kn_id,
                cypher=input_data.cypher,
                headers=headers_dict
            )
            
            logger.debug("Cypher查询API执行完成")
            return result
            
        except HTTPException:
            raise
        except (KnowledgeNetworkRetrievalError, KnowledgeNetworkParamError) as e:
            raise HTTPException(
                status_code=400 if isinstance(e, KnowledgeNetworkParamError) else 500,
                detail=e.json()
            )
    
    @classmethod
    def _build_cypher_description(cls, supported_templates: list) -> str:
        """
        从模板信息动态构建Cypher参数的描述文本
        
        Args:
            supported_templates: 支持的模板列表
            
        Returns:
            格式化的描述文本
        """
        # 基础描述 - 明确说明这是定制语法，不是标准Cypher
        description_parts = [
            "**重要：这是类Cypher语法模板，不是标准Neo4j Cypher！**\n\n",
            "本工具支持类Cypher语法查询知识网络，语法结构与标准Cypher类似，但有以下重要差异：\n",
            "1. 仅支持特定的查询模板（见下方），不是完整的Cypher语法\n",
            "2. 支持扩展运算符：KNN（向量搜索）、MATCH（全文搜索）\n",
            "3. 运算符使用方式与标准Cypher不同（特别是KNN、MATCH等）\n\n",
            "支持的查询模式：\n\n"
        ]
        
        # 遍历所有模板，生成描述
        for idx, template in enumerate(supported_templates, 1):
            template_type = template.get("template_type", "")
            template_desc = template.get("description", "")
            node_range = template.get("node_range", "")
            
            if template_type == "single_object":
                # 单个对象检索
                example = template.get("example", "")
                description_parts.append(f"**{idx}. 单个对象检索**\n")
                description_parts.append(f"{template_desc}\n\n")
                if example:
                    description_parts.append("示例：\n")
                    description_parts.append(f"```cypher\n{example}\n```\n\n")
            elif template_type == "relation_path":
                # 关系路径查询
                description_parts.append(f"**{idx}. 关系路径查询（{node_range}节点）**\n")
                description_parts.append(f"{template_desc}\n\n")
                
                # 添加多个示例
                if "examples" in template:
                    description_parts.append("示例：\n")
                    for example in template["examples"]:
                        description_parts.append(f"```cypher\n{example}\n```\n\n")
        
        # 添加语法说明 - 重点强调特殊运算符的使用方式
        description_parts.extend([
            "**支持的运算符（重要：与标准Cypher不同）**：\n\n",
            "**1. 标准比较运算符（SQL风格）**：\n",
            "- 格式：`a.field == 'value'` 或 `a.field != 'value'`\n",
            "- 支持：==, !=, >, <, >=, <=, LIKE\n",
            "- 示例：`WHERE a.disease_name == '发烧'` 或 `WHERE a.age > 30`\n\n",
            "**2. 扩展运算符（OpenSearch风格，本工具独有）**：\n",
            "- **KNN（向量相似度搜索）**：格式 `a.field KNN 'query_text'`（注意：不需要等号！）\n",
            "  - 示例：`WHERE a.disease_name KNN '发烧'`\n",
            "  - 用途：基于向量相似度进行语义搜索，默认k=50\n",
            "- **MATCH（全文搜索）**：格式 `a.field MATCH 'query_text'`（注意：不需要等号！）\n",
            "  - 示例：`WHERE a.symptom_name MATCH '咳嗽'`\n",
            "  - 用途：基于OpenSearch的全文搜索\n\n",
            "**语法规则说明**：\n",
            "- MATCH子句必需，用于指定查询的节点和关系模式\n",
            "- WHERE子句可选，用于过滤条件\n",
            "- RETURN子句必需，用于指定返回的字段（格式：a.field1, b.field2）\n",
            "- LIMIT子句可选，用于限制返回结果数量（如：LIMIT 10），未指定时使用默认值\n",
            "- 关系路径必须是单向的（箭头方向一致，如：->）\n",
            "- 节点变量名可自定义（如：a, b, c 或 person, school, major）\n",
            "- 关系变量名可自定义（如：r, r1, r2 或 belongs_to, has_major）\n\n",
            "**关键差异提醒（与标准Cypher不同）**：\n",
            "- KNN、MATCH运算符后面**不需要等号**，直接跟值：`a.field KNN 'value'`\n",
            "- 标准运算符需要等号：`a.field == 'value'`\n",
            "- WHERE子句中可以使用混合运算符，如：`WHERE a.name == '发烧' AND a.description KNN '症状'`\n",
            "- 本工具不支持标准Cypher的复杂语法（如OPTIONAL MATCH、UNWIND、聚合函数等）"
        ])
        
        return "".join(description_parts)
    
    @classmethod
    async def get_api_schema(cls):
        """获取API schema定义"""
        from .templates import CypherTemplateMatcher
        
        supported_templates = CypherTemplateMatcher.get_supported_templates()
        
        # 动态生成Cypher参数描述
        cypher_description = cls._build_cypher_description(supported_templates)
        
        # 构建示例
        examples = {}
        for template in supported_templates:
            # 对于关系路径模板，使用多个示例
            if template["template_type"] == "relation_path" and "examples" in template:
                for idx, example in enumerate(template["examples"], 1):
                    examples[f"{template['template_type']}_{idx}"] = {
                        "summary": f"{template['description']} (示例{idx})",
                        "description": template["description"],
                        "value": {
                            "kn_id": "kn_medical",
                            "cypher": example
                        }
                    }
                # 也添加一个主示例
                examples[template["template_type"]] = {
                    "summary": template["description"],
                    "description": template["description"],
                    "value": {
                        "kn_id": "kn_medical",
                        "cypher": template["examples"][0]
                    }
                }
            else:
                examples[template["template_type"]] = {
                    "summary": template["description"],
                    "description": template["description"],
                    "value": {
                        "kn_id": "kn_medical",
                        "cypher": template.get("example", "")
                    }
                }
        
        return {
            "post": {
                "summary": "cypher_query",
                "description": (
                    "使用类Cypher语法模板查询知识网络（注意：不是标准Neo4j Cypher，是定制语法）。\n"
                    "支持：\n"
                    "1. 单个对象检索：MATCH (a:ObjectType) WHERE ... RETURN ...\n"
                    "2. 关系路径查询（2-10节点）：MATCH (a:TypeA)-[r1:RelType1]->(b:TypeB)-[r2:RelType2]->(c:TypeC)... WHERE ... RETURN ...\n\n"
                    "特殊支持：KNN（向量搜索）、MATCH（全文搜索）等扩展运算符，"
                    "使用方式与标准Cypher不同（KNN/MATCH后面不需要等号，直接跟值）。"
                ),
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
                                    "cypher": {
                                        "type": "string",
                                        "description": cypher_description
                                    }
                                },
                                "required": ["kn_id", "cypher"]
                            },
                            "examples": examples
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
                        "description": "查询成功",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "description": "检索结果（meta + table格式）",
                                    "properties": {
                                        "meta": {
                                            "type": "object",
                                            "description": "请求与执行元信息"
                                        },
                                        "table": {
                                            "type": "object",
                                            "description": "结果表（类SQL格式）",
                                            "properties": {
                                                "columns": {
                                                    "type": "array",
                                                    "items": {"type": "string"},
                                                    "description": "列名数组，格式：object_type.field_name"
                                                },
                                                "rows": {
                                                    "type": "array",
                                                    "items": {
                                                        "type": "array",
                                                        "items": {}
                                                    },
                                                    "description": "行数据二维数组"
                                                }
                                            },
                                            "required": ["columns", "rows"]
                                        }
                                    },
                                    "required": ["meta", "table"]
                                }
                            }
                        }
                    },
                    "400": {
                        "description": "参数错误或Cypher语法不支持",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {
                                            "type": "string",
                                            "description": "错误信息"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

