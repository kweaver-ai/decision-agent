# -*- coding: utf-8 -*-
"""
Cypher查询转换器
将解析后的Cypher查询转换为知识网络检索参数
"""

import re
from typing import Dict, Any, List, Optional

from data_retrieval.errors import KnowledgeNetworkParamError

from .parser import CypherParseResult
from .templates import QueryType
from ..relation_path_retrieval_tool import (
    RelationPathRetrievalInput,
    RelationTypePathConfig,
    ObjectTypeConfig,
    RelationTypeConfig,
    ConditionConfig,
    SingleCondition
)


class WhereConditionParser:
    """WHERE条件解析器"""
    
    # 支持的运算符映射
    # SQL风格操作符：==, !=, >, <, >=, <=, like
    # OpenSearch风格操作符：match, knn
    OPERATOR_MAP = {
        # SQL风格比较操作符
        "==": "==",
        "!=": "!=",
        ">": ">",
        "<": "<",
        ">=": ">=",
        "<=": "<=",
        "=": "==",  # 兼容等号
        
        # SQL风格模糊匹配
        "LIKE": "like",
        "like": "like",
        
        # OpenSearch风格文本匹配
        "MATCH": "match",
        "match": "match",
        
        # OpenSearch风格向量搜索
        "KNN": "knn",
        "knn": "knn",
    }
    
    # 需要特殊处理的操作符（可能需要额外参数）
    SPECIAL_OPERATORS = {"knn"}
    
    # KNN默认参数
    KNN_DEFAULT_K = 50
    
    @classmethod
    def parse_conditions(
        cls,
        where_clause: Optional[str],
        node_var: str
    ) -> List[SingleCondition]:
        """
        解析WHERE子句中指定节点的条件
        
        支持的操作符：
        - SQL风格：==, !=, >, <, >=, <=, LIKE
        - OpenSearch风格：MATCH, KNN
        
        Args:
            where_clause: WHERE子句内容
            node_var: 节点变量名
            
        Returns:
            SingleCondition列表
        """
        if not where_clause:
            return []
        
        conditions = []
        
        # 按操作符类型分别处理，因为不同操作符的值格式可能不同
        # 1. 先处理特殊操作符（KNN、MATCH等），它们后面直接跟值，不需要等号
        # 2. 再处理标准比较操作符（==, >, <等）
        
        # 模式1：特殊操作符（KNN, MATCH）- 格式：field OPERATOR 'value'
        # 这些操作符后面直接跟值，不需要等号
        # 值可以是引号包裹的字符串或非引号值
        special_ops_pattern = rf"{re.escape(node_var)}\.(\w+)\s+(KNN|knn|MATCH|match)\s+((?:[\"'])(?:[^\"']*)(?:[\"'])|[^\s\"']+)(?=\s+AND|\s+OR|\s*$)"
        special_matches = re.finditer(special_ops_pattern, where_clause, re.IGNORECASE)
        
        # 记录已匹配的位置，避免重复匹配
        matched_positions = set()
        
        for match in special_matches:
            start, end = match.span()
            matched_positions.add((start, end))
            
            field = match.group(1)
            operator = match.group(2).upper() if match.group(2).upper() in ["KNN", "MATCH"] else match.group(2).lower()
            value_str = match.group(3).strip()
            
            # 转换运算符
            if operator not in cls.OPERATOR_MAP:
                continue
            
            mapped_operator = cls.OPERATOR_MAP[operator]
            
            # 解析值
            value = cls._parse_value(value_str)
            
            condition = SingleCondition(
                field=field,
                operation=mapped_operator,
                value=value,
                value_from="const"
            )
            conditions.append(condition)
        
        # 模式2：标准比较操作符（==, !=, >, <, >=, <=, LIKE） - 格式：field OPERATOR 'value'
        # 排除已经匹配的特殊操作符位置
        standard_ops = ["==", "!=", ">", "<", ">=", "<=", "=", "LIKE", "like"]
        standard_pattern = rf"{re.escape(node_var)}\.(\w+)\s*({'|'.join(re.escape(op) for op in standard_ops)})\s*((?:[\"'])(?:[^\"']*)(?:[\"'])|[^\s\"']+)(?=\s+AND|\s+OR|\s*$)"
        standard_matches = re.finditer(standard_pattern, where_clause, re.IGNORECASE)
        
        for match in standard_matches:
            start, end = match.span()
            # 检查是否与已匹配的特殊操作符位置重叠
            is_overlapped = any(start < pos_end and end > pos_start for pos_start, pos_end in matched_positions)
            if is_overlapped:
                continue
            
            field = match.group(1)
            operator = match.group(2)
            value_str = match.group(3).strip()
            
            # 转换运算符
            if operator not in cls.OPERATOR_MAP:
                raise KnowledgeNetworkParamError(
                    detail={
                        "error": f"不支持的运算符：{operator}",
                        "supported_operators": list(cls.OPERATOR_MAP.keys()),
                        "field": field,
                        "node_var": node_var
                    }
                )
            
            mapped_operator = cls.OPERATOR_MAP[operator]
            
            # 解析值
            value = cls._parse_value(value_str)
            
            condition = SingleCondition(
                field=field,
                operation=mapped_operator,
                value=value,
                value_from="const"
            )
            conditions.append(condition)
        
        return conditions
    
    @classmethod
    def _parse_value(cls, value_str: str) -> Any:
        """
        解析值字符串，尝试转换为合适的类型
        
        Args:
            value_str: 值的字符串表示
            
        Returns:
            转换后的值（int/float/str/None）
        """
        value_str = value_str.strip()
        
        # 去除引号
        if (value_str.startswith("'") and value_str.endswith("'")) or \
           (value_str.startswith('"') and value_str.endswith('"')):
            return value_str[1:-1]
        
        # 尝试转换为数字
        try:
            if '.' in value_str:
                return float(value_str)
            else:
                return int(value_str)
        except ValueError:
            pass
        
        # 处理特殊值
        if value_str.upper() == "NULL":
            return None
        
        # 返回字符串
        return value_str


class CypherConverter:
    """Cypher查询转换器"""
    
    @classmethod
    def convert_to_object_retrieval_params(
        cls,
        kn_id: str,
        parsed: CypherParseResult
    ) -> Dict[str, Any]:
        """
        转换为单个对象检索参数
        
        Args:
            kn_id: 知识网络ID
            parsed: 解析结果
            
        Returns:
            对象检索参数字典，包含：
            - kn_id: 知识网络ID
            - object_type_id: 对象类型ID
            - condition: 查询条件
            - limit: 结果数量限制
        """
        if parsed.query_type != QueryType.SINGLE_OBJECT:
            raise ValueError("只有单个对象查询才能转换为对象检索参数")
        
        if not parsed.nodes:
            raise ValueError("解析结果中没有节点信息")
        
        node = parsed.nodes[0]
        
        # 解析WHERE条件
        conditions = []
        if parsed.where_clause:
            conditions = WhereConditionParser.parse_conditions(
                parsed.where_clause,
                node.var
            )
        
        # 构建condition配置
        condition_config = None
        if conditions:
            sub_conditions_list = []
            for c in conditions:
                condition_dict = {
                        "field": c.field,
                        "operation": c.operation,
                        "value": c.value,
                        "value_from": c.value_from
                    }
                # KNN操作符需要额外的limit_key和limit_value参数
                if c.operation == "knn":
                    condition_dict["limit_key"] = "k"
                    condition_dict["limit_value"] = str(WhereConditionParser.KNN_DEFAULT_K)
                # like操作符的value需要在调用底层接口时添加%，Cypher语句中可以不加
                elif c.operation == "like" and isinstance(c.value, str):
                    # 如果value中没有%，则自动添加前后%
                    if "%" not in c.value:
                        condition_dict["value"] = f"%{c.value}%"
                
                sub_conditions_list.append(condition_dict)
            
            condition_config = {
                "operation": "and",
                "sub_conditions": sub_conditions_list
            }
        
        # 导入ObjectRetrievalTool以使用其默认值和上限
        from .object_retrieval_tool import ObjectRetrievalTool
        
        # 使用ObjectRetrievalTool的默认值和上限限制
        effective_limit = (
            parsed.limit 
            if parsed.limit is not None 
            else ObjectRetrievalTool.DEFAULT_LIMIT
        )
        effective_limit = min(effective_limit, ObjectRetrievalTool.MAX_REQUEST_LIMIT)
        
        return {
            "kn_id": kn_id,
            "object_type_id": node.type_id,
            "condition": condition_config,
            "limit": effective_limit,
            "properties": cls._extract_properties_for_node(
                parsed.return_properties,
                node.var
            )
        }
    
    @classmethod
    def convert_to_relation_path_params(
        cls,
        kn_id: str,
        parsed: CypherParseResult
    ) -> RelationPathRetrievalInput:
        """
        转换为关系路径检索参数
        
        Args:
            kn_id: 知识网络ID
            parsed: 解析结果
            
        Returns:
            RelationPathRetrievalInput对象
        """
        if parsed.query_type != QueryType.RELATION_PATH:
            raise ValueError("只有关系路径查询才能转换为关系路径检索参数")
        
        # 导入RelationPathRetrievalTool以使用其默认值和上限
        from ..relation_path_retrieval_tool import RelationPathRetrievalTool
        
        # 使用RelationPathRetrievalTool的默认值和上限限制
        effective_path_limit = (
            parsed.limit 
            if parsed.limit is not None 
            else RelationPathRetrievalTool.DEFAULT_LIMIT
        )
        effective_path_limit = min(effective_path_limit, RelationPathRetrievalTool.MAX_REQUEST_LIMIT)
        
        path_limit = effective_path_limit
        
        # ========= 临时方案开始 =========
        # 说明：
        #   当前知识网络子图/路径检索接口在底层是「无向边」，但需要我们显式指定从哪个对象类型作为起点。
        #   现状：如果第一个节点没有条件，而后面节点有条件，则会先从首节点随机采样大量实例，
        #         再看这些实例是否与有条件节点存在关系，容易在第一步就把正确答案过滤掉。
        #
        #   临时解决方案：
        #     - 只要检测到「第一个节点没有 WHERE 条件」，就将整条路径反转：
        #         * 节点顺序反转
        #         * 关系顺序反转，并按新的节点顺序重新设置 source/target
        #     - 这样在典型场景中（如从药品查疾病），会自然从“带条件的末尾节点”作为起点发起路径查询，
        #       提升召回完整性。
        #
        #   注意：
        #     - 这是一个「临时救火逻辑」，依赖于当前知识网络接口缺少“按条件优先筛选起点”的能力。
        #     - **一旦底层接口支持基于条件的起点选择，应当移除本段逻辑，直接使用 parsed.nodes 的原始顺序。**
        #
        #   移除方式（未来改造后）：
        #     - 删除 should_reverse / nodes_seq / relation_type_ids 的判断和构造逻辑，
        #     - 将 nodes_seq 替换为 parsed.nodes，
        #     - 将 relation_type_ids 替换为 [rel.type_id for rel in parsed.relations]。
        # ========= 临时方案结束 =========
        nodes_seq = list(parsed.nodes)
        should_reverse = False
        if nodes_seq:
            # 第一个节点的 WHERE 条件（如果没有 WHERE 子句或未命中当前节点，返回空列表）
            first_node = nodes_seq[0]
            first_conditions = WhereConditionParser.parse_conditions(
                parsed.where_clause,
                first_node.var
            ) if parsed.where_clause else []
            if not first_conditions and len(nodes_seq) >= 2:
                should_reverse = True
        
        if should_reverse:
            # 反转节点顺序
            nodes_seq = list(reversed(nodes_seq))
            # 关系类型 ID 也按反向顺序排列，使之与反转后的节点顺序对齐
            relation_type_ids = [rel.type_id for rel in reversed(parsed.relations)]
        else:
            # 保持原始顺序
            relation_type_ids = [rel.type_id for rel in parsed.relations]
        
        # 构建对象类型配置
        object_types = []
        for node in nodes_seq:
            # 解析WHERE条件
            conditions = []
            if parsed.where_clause:
                conditions = WhereConditionParser.parse_conditions(
                    parsed.where_clause,
                    node.var
                )
            
            # 提取该节点的返回属性
            properties = cls._extract_properties_for_node(
                parsed.return_properties,
                node.var
            )
            
            # 构建对象类型配置
            # 对于关系路径查询，LIMIT 只作用在路径级别（RelationTypePathConfig.limit），
            # object_types 本身不再单独传递 limit，交给底层服务按默认行为处理。
            obj_config = ObjectTypeConfig(
                id=node.type_id,
                properties=properties if properties else None,
                # 显式设置为 None，避免后续序列化时带出对象级 limit 字段
                limit=None
            )
            
            # 如果有条件，添加condition
            if conditions:
                # 处理KNN操作符的特殊参数，需要在序列化时添加limit_key和limit_value
                # 由于ConditionConfig不允许额外字段，我们需要构建字典格式的condition
                sub_conditions_dicts = []
                for c in conditions:
                    sub_cond = {
                        "field": c.field,
                        "operation": c.operation,
                        "value": c.value,
                        "value_from": c.value_from
                    }
                    # KNN操作符需要额外的limit_key和limit_value参数
                    if c.operation == "knn":
                        sub_cond["limit_key"] = "k"
                        sub_cond["limit_value"] = str(WhereConditionParser.KNN_DEFAULT_K)
                    # like操作符的value需要在调用底层接口时添加%，Cypher语句中可以不加
                    elif c.operation == "like" and isinstance(c.value, str):
                        # 如果value中没有%，则自动添加前后%
                        if "%" not in c.value:
                            sub_cond["value"] = f"%{c.value}%"
                    sub_conditions_dicts.append(sub_cond)
                
                # 构建字典格式的condition（在API调用时会转换为JSON）
                obj_config.condition = {
                    "operation": "and",
                    "sub_conditions": sub_conditions_dicts
                }
            
            object_types.append(obj_config)
        
        # 构建关系类型配置
        relation_types = []
        # 此处不再依赖 ParsedRelation 中的 source_var/target_var，
        # 而是基于（可能已被反转的）节点顺序和关系类型 ID 顺序来构造 source/target。
        for idx, rel_type_id in enumerate(relation_type_ids):
            # 节点序列保证为线性路径：关系数 = 节点数 - 1
            if idx + 1 >= len(nodes_seq):
                break
            source_node = nodes_seq[idx]
            target_node = nodes_seq[idx + 1]
            relation_types.append(RelationTypeConfig(
                relation_type_id=rel_type_id,
                source_object_type_id=source_node.type_id,
                target_object_type_id=target_node.type_id
            ))
        
        # 构建RelationTypePathConfig
        # 使用解析出的LIMIT值（已在上面获取）
        relation_path = RelationTypePathConfig(
            object_types=object_types,
            relation_types=relation_types,
            limit=path_limit
        )
        
        # 构建最终输入
        return RelationPathRetrievalInput(
            kn_id=kn_id,
            relation_type_paths=[relation_path]
        )
    
    @classmethod
    def _extract_properties_for_node(
        cls,
        return_properties: List,
        node_var: str
    ) -> List[str]:
        """
        提取指定节点的返回属性列表
        
        Args:
            return_properties: 所有返回属性
            node_var: 节点变量名
            
        Returns:
            属性字段名列表
        """
        return [
            prop.field
            for prop in return_properties
            if prop.node_var == node_var
        ]

