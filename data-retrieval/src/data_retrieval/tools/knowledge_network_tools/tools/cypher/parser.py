# -*- coding: utf-8 -*-
"""
Cypher查询解析器
解析Cypher语句的各个部分：节点、关系、WHERE条件、RETURN属性
"""

import re
from typing import Dict, Any, List, Optional

from data_retrieval.errors import KnowledgeNetworkParamError

from .templates import CypherTemplateMatcher, QueryType


class ParsedNode:
    """解析后的节点信息"""
    
    def __init__(self, var: str, type_id: str):
        self.var = var
        self.type_id = type_id
    
    def __repr__(self):
        return f"Node(var={self.var}, type={self.type_id})"


class ParsedRelation:
    """解析后的关系信息"""
    
    def __init__(self, var: str, type_id: str, source_var: str, target_var: str):
        self.var = var
        self.type_id = type_id
        self.source_var = source_var
        self.target_var = target_var
    
    def __repr__(self):
        return f"Relation(var={self.var}, type={self.type_id}, {self.source_var}->{self.target_var})"


class ParsedProperty:
    """解析后的属性信息"""
    
    def __init__(self, node_var: str, field: str):
        self.node_var = node_var
        self.field = field
    
    def __repr__(self):
        return f"Property({self.node_var}.{self.field})"


class CypherParseResult:
    """Cypher解析结果"""
    
    def __init__(
        self,
        query_type: QueryType,
        nodes: List[ParsedNode],
        relations: List[ParsedRelation],
        where_clause: Optional[str],
        return_properties: List[ParsedProperty],
        limit: Optional[int] = None
    ):
        self.query_type = query_type
        self.nodes = nodes
        self.relations = relations
        self.where_clause = where_clause
        self.return_properties = return_properties
        self.limit = limit  # LIMIT子句的值，如果未指定则为None


class CypherParser:
    """Cypher查询解析器"""
    
    @classmethod
    def parse(cls, cypher: str) -> CypherParseResult:
        """
        解析Cypher查询语句
        
        Args:
            cypher: Cypher查询语句
            
        Returns:
            CypherParseResult对象
            
        Raises:
            KnowledgeNetworkParamError: 当Cypher语法不符合要求时
        """
        cypher = cypher.strip()
        
        # 1. 匹配模板
        try:
            match_result = CypherTemplateMatcher.match_template(cypher)
        except ValueError as e:
            raise KnowledgeNetworkParamError(
                detail={
                    "error": str(e),
                    "supported_templates": CypherTemplateMatcher.get_supported_templates()
                }
            )
        
        template = match_result["template"]
        match = match_result["match"]
        query_type = match_result["query_type"]
        
        # 2. 解析节点和关系
        nodes, relations = cls._parse_nodes_and_relations(
            template.template_type,
            query_type,
            match,
            cypher
        )
        
        # 3. 解析WHERE子句
        where_clause = cls._extract_where_clause(cypher)
        
        # 4. 解析RETURN子句
        return_properties = cls._parse_return_clause(cypher)
        
        # 5. 解析LIMIT子句（可选）
        limit = cls._extract_limit_clause(cypher, match.groups())
        
        return CypherParseResult(
            query_type=query_type,
            nodes=nodes,
            relations=relations,
            where_clause=where_clause,
            return_properties=return_properties,
            limit=limit
        )
    
    @classmethod
    def _parse_nodes_and_relations(
        cls,
        template_type: str,
        query_type: QueryType,
        match: re.Match,
        cypher: str
    ) -> tuple[List[ParsedNode], List[ParsedRelation]]:
        """
        从正则匹配结果中解析节点和关系（优化版本，支持动态解析）
        
        Args:
            template_type: 模板类型
            query_type: 查询类型
            match: 正则表达式匹配对象
            cypher: 原始Cypher查询语句
            
        Returns:
            (节点列表, 关系列表)
        """
        nodes = []
        relations = []
        
        if template_type == "single_object":
            # 单个对象：groups = (var, type_id, where_clause, return_clause)
            groups = match.groups()
            nodes.append(ParsedNode(var=groups[0], type_id=groups[1]))
        
        elif template_type == "relation_path":
            # 关系路径：动态解析任意长度的路径
            # 从原始Cypher查询中提取MATCH子句部分（到WHERE或RETURN之前）
            match_start = match.start()
            match_end = match.end()
            
            # 从匹配开始位置往前找到MATCH关键字，往后找到WHERE或RETURN
            match_content = cypher[match_start:match_end]
            
            # 提取MATCH子句的内容（MATCH后面的部分，到WHERE或RETURN之前）
            # 匹配模式会匹配到WHERE或RETURN，我们需要提取MATCH到这些关键字之间的部分
            match_part_match = re.search(
                r"MATCH\s+(.+?)(?:\s+WHERE|\s+RETURN)",
                cypher[match_start:],
                re.IGNORECASE | re.DOTALL
            )
            
            if match_part_match:
                match_part = match_part_match.group(1).strip()
            else:
                # 如果没有WHERE或RETURN，直接使用匹配到的内容（去掉MATCH关键字）
                match_part = re.sub(r"^MATCH\s+", "", match_content, flags=re.IGNORECASE).strip()
            
            # 使用正则表达式提取所有节点：(var:type)
            node_pattern = re.compile(r"\((\w+):(\w+)\)")
            node_matches = node_pattern.finditer(match_part)
            
            # 构建节点列表
            for node_match in node_matches:
                var, type_id = node_match.groups()
                nodes.append(ParsedNode(var=var, type_id=type_id))
            
            # 使用正则表达式提取所有关系：[var:type]
            rel_pattern = re.compile(r"\[(\w+):(\w+)\]")
            rel_matches = rel_pattern.finditer(match_part)
            
            # 构建关系列表（关系的source和target是相邻的节点）
            rel_list = [rel_match.groups() for rel_match in rel_matches]
            
            # 确保关系数量和节点数量匹配（关系数 = 节点数 - 1）
            if len(rel_list) != len(nodes) - 1:
                raise KnowledgeNetworkParamError(
                    detail={
                        "error": f"关系数量({len(rel_list)})与节点数量({len(nodes)})不匹配",
                        "hint": "关系路径中，关系数量应该等于节点数量减1"
                    }
                )
            
            # 构建关系对象（每个关系连接相邻的两个节点）
            for i, (rel_var, rel_type) in enumerate(rel_list):
                relations.append(ParsedRelation(
                    var=rel_var,
                    type_id=rel_type,
                    source_var=nodes[i].var,
                    target_var=nodes[i + 1].var
                ))
        
        return nodes, relations
    
    @classmethod
    def _extract_where_clause(cls, cypher: str) -> Optional[str]:
        """
        提取WHERE子句内容
        
        Args:
            cypher: Cypher查询语句
            
        Returns:
            WHERE子句内容（不包含WHERE关键字），如果不存在返回None
        """
        # 匹配 WHERE ... RETURN 之间的内容
        where_match = re.search(
            r"WHERE\s+(.+?)(?:\s+RETURN|\s*$)",
            cypher,
            re.IGNORECASE | re.DOTALL
        )
        if where_match:
            return where_match.group(1).strip()
        return None
    
    @classmethod
    def _parse_return_clause(cls, cypher: str) -> List[ParsedProperty]:
        """
        解析RETURN子句，提取返回的属性列表
        
        Args:
            cypher: Cypher查询语句
            
        Returns:
            属性列表
            
        Raises:
            KnowledgeNetworkParamError: 当RETURN子句格式错误时
        """
        return_match = re.search(
            r"RETURN\s+(.+?)$",
            cypher,
            re.IGNORECASE | re.DOTALL
        )
        
        if not return_match:
            raise KnowledgeNetworkParamError(
                detail={
                    "error": "Cypher查询缺少RETURN子句",
                    "hint": "请在查询末尾添加 RETURN 子句，例如：RETURN a.field1, b.field2"
                }
            )
        
        return_str = return_match.group(1).strip()
        properties = []
        
        # 按逗号分割属性
        for prop in return_str.split(','):
            prop = prop.strip()
            if not prop:
                continue
            
            # 匹配格式：node_var.field_name 或 node_var.field_name AS alias
            match = re.match(r"(\w+)\.(\w+)(?:\s+AS\s+\w+)?", prop)
            if match:
                properties.append(ParsedProperty(
                    node_var=match.group(1),
                    field=match.group(2)
                ))
            else:
                raise KnowledgeNetworkParamError(
                    detail={
                        "error": f"RETURN子句格式错误：{prop}",
                        "hint": "返回属性格式应为：node_var.field_name，例如：a.field1, b.field2",
                        "invalid_property": prop
                    }
                )
        
        if not properties:
            raise KnowledgeNetworkParamError(
                detail={
                    "error": "RETURN子句中至少需要指定一个返回属性",
                    "hint": "例如：RETURN a.field1, b.field2"
                }
            )
        
        return properties
    
    @classmethod
    def _extract_limit_clause(cls, cypher: str, groups: tuple) -> Optional[int]:
        """
        解析LIMIT子句，提取LIMIT值
        
        Args:
            cypher: Cypher查询语句
            groups: 正则表达式匹配的组（最后一个组可能是LIMIT值）
            
        Returns:
            LIMIT值（整数），如果不存在返回None
        """
        # LIMIT值应该在正则匹配的最后一个组中（如果存在）
        if groups and len(groups) > 0:
            # 检查最后一个组是否是LIMIT值（数字）
            last_group = groups[-1]
            if last_group and isinstance(last_group, str) and last_group.isdigit():
                try:
                    return int(last_group)
                except ValueError:
                    pass
        
        # 如果没有通过正则匹配到，尝试直接从查询语句中提取
        # 匹配格式：LIMIT n（在RETURN子句之后）
        limit_match = re.search(
            r"RETURN\s+.+?\s+LIMIT\s+(\d+)\s*$",
            cypher,
            re.IGNORECASE | re.DOTALL
        )
        if limit_match:
            try:
                return int(limit_match.group(1))
            except (ValueError, IndexError):
                pass
        
        return None

