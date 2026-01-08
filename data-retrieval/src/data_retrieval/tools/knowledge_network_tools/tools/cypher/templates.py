# -*- coding: utf-8 -*-
"""
Cypher查询模板定义和匹配器
定义支持的Cypher查询模板，并提供模板匹配功能
优化版本：使用通用模式匹配关系路径，支持2-10节点
"""

import re
from typing import Dict, Any, Optional, List
from enum import Enum


class QueryType(Enum):
    """查询类型枚举"""
    SINGLE_OBJECT = "single_object"  # 单个对象检索
    RELATION_PATH = "relation_path"  # 关系路径检索


class CypherTemplate:
    """Cypher查询模板定义"""
    
    def __init__(
        self,
        template_type: str,
        query_type: QueryType,
        pattern: str,
        description: str,
        min_nodes: int = None,
        max_nodes: int = None,
        example: str = None
    ):
        """
        初始化模板
        
        Args:
            template_type: 模板类型标识（如 "single_object", "relation_path"）
            query_type: 查询类型
            pattern: 正则表达式模式
            description: 模板描述
            min_nodes: 最小节点数量
            max_nodes: 最大节点数量
            example: 示例查询
        """
        self.template_type = template_type
        self.query_type = query_type
        self.pattern = re.compile(pattern, re.IGNORECASE | re.DOTALL)
        self.description = description
        self.min_nodes = min_nodes
        self.max_nodes = max_nodes
        self.example = example


class CypherTemplateMatcher:
    """Cypher模板匹配器 - 优化版本"""
    
    # 节点模式：\((\w+):(\w+)\)
    NODE_PATTERN = r"\((\w+):(\w+)\)"
    
    # 关系模式：\[(\w+):(\w+)\]
    RELATION_PATTERN = r"\[(\w+):(\w+)\]"
    
    # 关系路径查询支持的最大节点数（可根据实际需求调整）
    MAX_PATH_NODES = 10
    
    # 支持的模板定义
    TEMPLATES: List[CypherTemplate] = [
        # 单个对象检索模板（支持可选的LIMIT子句）
        CypherTemplate(
            template_type="single_object",
            query_type=QueryType.SINGLE_OBJECT,
            pattern=rf"MATCH\s+{NODE_PATTERN}\s*(?:WHERE\s+(.+?))?\s+RETURN\s+(.+?)(?:\s+LIMIT\s+(\d+))?\s*$",
            description="单个对象检索：MATCH (a:ObjectType) WHERE a.field == 'value' RETURN a.field1, a.field2 [LIMIT n]",
            min_nodes=1,
            max_nodes=1,
            example="MATCH (a:disease) WHERE a.disease_name == '发烧' RETURN a.disease_name, a.age LIMIT 10"
        ),
        
        # 通用关系路径模板（支持2-10节点，支持可选的LIMIT子句）
        # 模式：(节点)-[关系]->(节点) 重复1-9次（总共2-10节点）
        CypherTemplate(
            template_type="relation_path",
            query_type=QueryType.RELATION_PATH,
            pattern=(
                rf"MATCH\s+{NODE_PATTERN}"  # 第一个节点
                rf"(?:-{RELATION_PATTERN}->{NODE_PATTERN}){{1,{MAX_PATH_NODES - 1}}}"  # 1到(MAX-1)个关系-节点对
                r"\s*(?:WHERE\s+(.+?))?\s*RETURN\s+(.+?)(?:\s+LIMIT\s+(\d+))?\s*$"
            ),
            description=f"关系路径查询：MATCH (a:TypeA)-[r1:RelType1]->(b:TypeB)-[r2:RelType2]->(c:TypeC)... WHERE ... RETURN ... [LIMIT n] (支持2-{MAX_PATH_NODES}节点)",
            min_nodes=2,
            max_nodes=MAX_PATH_NODES,
            example="MATCH (a:disease)-[r:has_symptom]->(b:symptom) WHERE a.disease_name == '上气道梗阻' RETURN a.disease_name, b.symptom_name LIMIT 20"
        ),
    ]
    
    @classmethod
    def match_template(cls, cypher: str) -> Optional[Dict[str, Any]]:
        """
        匹配Cypher查询到支持的模板
        
        Args:
            cypher: Cypher查询语句
            
        Returns:
            匹配结果字典，包含：
            - template: CypherTemplate对象
            - match: re.Match对象
            - query_type: 查询类型
            - node_count: 节点数量（关系路径查询时）
            
        Raises:
            抛出详细的错误信息说明不匹配的原因
        """
        cypher = cypher.strip()
        
        # 先尝试单个对象模板
        single_object_template = cls.TEMPLATES[0]
        match = single_object_template.pattern.search(cypher)
        if match:
            return {
                "template": single_object_template,
                "match": match,
                "query_type": QueryType.SINGLE_OBJECT,
                "node_count": 1
            }
        
        # 再尝试关系路径模板
        relation_path_template = cls.TEMPLATES[1]
        match = relation_path_template.pattern.search(cypher)
        if match:
            # 计算实际节点数量
            match_str = match.group(0)
            node_count = cls._count_nodes_in_match(match_str)
            
            # 验证节点数量是否在支持范围内
            if node_count < relation_path_template.min_nodes or \
               node_count > relation_path_template.max_nodes:
                raise ValueError(
                    f"关系路径节点数量 {node_count} 不在支持范围内 "
                    f"({relation_path_template.min_nodes}-{relation_path_template.max_nodes}节点)。"
                )
            
            return {
                "template": relation_path_template,
                    "match": match,
                "query_type": QueryType.RELATION_PATH,
                "node_count": node_count
                }
        
        # 没有匹配到任何模板，生成详细的错误信息
        raise ValueError(
            cls._generate_error_message(cypher)
        )
    
    @classmethod
    def _count_nodes_in_match(cls, matched_str: str) -> int:
        """
        计算匹配字符串中的节点数量
        
        Args:
            matched_str: 匹配的字符串
            
        Returns:
            节点数量
        """
        return len(re.findall(cls.NODE_PATTERN, matched_str))
    
    @classmethod
    def _generate_error_message(cls, cypher: str) -> str:
        """生成详细的错误提示信息"""
        single_template = cls.TEMPLATES[0]
        path_template = cls.TEMPLATES[1]
        
        return (
            "不支持的Cypher查询模式。\n\n"
            "支持的查询模板：\n\n"
            f"【{single_template.template_type}】\n"
            f"  描述: {single_template.description}\n"
            f"  示例: {single_template.example}\n\n"
            f"【{path_template.template_type}】\n"
            f"  描述: {path_template.description}\n"
            f"  节点范围: {path_template.min_nodes}-{path_template.max_nodes}节点\n"
            f"  示例: {path_template.example}\n\n"
            f"您输入的查询: {cypher[:200]}\n\n"
            "请检查：\n"
            "1. MATCH子句的格式是否正确\n"
            f"2. 节点数量是否在1-{path_template.max_nodes}个之间\n"
            "3. 关系路径是否都是单向（箭头方向一致）\n"
            "4. RETURN子句是否存在且格式正确"
        )
    
    @classmethod
    def get_supported_templates(cls) -> List[Dict[str, Any]]:
        """获取所有支持的模板信息（用于API文档）"""
        single_template = cls.TEMPLATES[0]
        path_template = cls.TEMPLATES[1]
        
        # 为文档生成几个典型的关系路径示例
        path_examples = [
            "MATCH (a:disease)-[r:has_symptom]->(b:symptom) WHERE a.disease_name == '上气道梗阻' RETURN a.disease_name, b.symptom_name",
            "MATCH (a:person)-[r1:belongs_to]->(b:school)-[r2:has_major]->(c:major) WHERE a.name == '张三' RETURN a.name, b.school_name, c.major_name",
            "MATCH (a:person)-[r1:belongs_to]->(b:school)-[r2:has_major]->(c:major)-[r3:taught_by]->(d:teacher) WHERE a.name == '张三' RETURN a.name, b.school_name, c.major_name, d.teacher_name"
        ]
        
        return [
            {
                "template_type": single_template.template_type,
                "query_type": single_template.query_type.value,
                "description": single_template.description,
                "node_range": f"{single_template.min_nodes}",
                "example": single_template.example
            },
            {
                "template_type": path_template.template_type,
                "query_type": path_template.query_type.value,
                "description": path_template.description,
                "node_range": f"{path_template.min_nodes}-{path_template.max_nodes}",
                "examples": path_examples
            }
        ]

