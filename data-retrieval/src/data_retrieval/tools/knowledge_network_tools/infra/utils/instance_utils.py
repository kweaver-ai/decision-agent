# -*- coding: utf-8 -*-
"""
实例工具模块
提供提取实例ID、名称和唯一标识符的公共方法
"""

from typing import Dict, Any, List, Optional
from data_retrieval.logs.logger import logger


class InstanceUtils:
    """实例工具类"""
    
    @staticmethod
    def extract_instance_id(
        instance_data: Dict[str, Any],
        primary_keys: List[str],
        object_type_id: str = "",
        raise_on_error: bool = False,
        combine_primary_keys: bool = True
    ) -> Optional[str]:
        """
        从实例数据中提取instance_id
        
        Args:
            instance_data: 实例数据字典
            primary_keys: 主键字段名列表
            object_type_id: 对象类型ID（用于错误提示）
            raise_on_error: 如果无法提取ID是否抛出异常
            combine_primary_keys: 是否组合多个主键（True：组合所有非空主键，False：只使用第一个主键）
            
        Returns:
            实例ID，如果无法提取返回None
        """
        if not primary_keys or not isinstance(primary_keys, list):
            if raise_on_error:
                raise ValueError(
                    f"对象类型 {object_type_id} 的主键字段列表不能为空，"
                    f"必须从schema中获取primary_keys"
                )
            return None
        
        # 方案：根据主键数量决定是否组合
        # 如果只有一个主键，直接使用该字段的值（唯一标识）
        # 如果有多个主键，组合所有非空的主键字段（复合主键）
        if len(primary_keys) == 1:
            # 单个主键：直接使用该字段的值
            pk_field = primary_keys[0]
            if pk_field in instance_data:
                pk_value = instance_data.get(pk_field)
                if pk_value is not None and pk_value != "":
                    instance_id = str(pk_value)
                    return instance_id
        elif combine_primary_keys and len(primary_keys) > 1:
            # 多个主键：组合所有非空的主键字段
            pk_values = []
            for pk_field in primary_keys:
                if pk_field in instance_data:
                    pk_value = instance_data.get(pk_field)
                    # 只包含非空值
                    if pk_value is not None and pk_value != "":
                        pk_values.append(str(pk_value))
            
            if pk_values:
                instance_id = ",".join(pk_values)
                return instance_id
        else:
            # 兼容旧逻辑：只使用第一个非空的主键字段
            for pk_field in primary_keys:
                if pk_field in instance_data and instance_data.get(pk_field):
                    instance_id = instance_data.get(pk_field)
                    return instance_id
        
        # 如果没有primary_keys或都为空，尝试从常见字段获取
        instance_id = instance_data.get("instance_id") or instance_data.get("id")
        if instance_id:
            return instance_id
        
        if raise_on_error:
            raise ValueError(
                f"对象类型 {object_type_id} 的返回数据中所有主键字段 {primary_keys} "
                f"都为空或不存在，数据: {instance_data}"
            )
        
        logger.warning(
            f"对象类型 {object_type_id} 的实例无法提取instance_id，"
            f"primary_keys={primary_keys}, 实例keys: {list(instance_data.keys())[:10]}"
        )
        return None
    
    @staticmethod
    def extract_instance_name(
        instance_data: Dict[str, Any],
        display_key: Optional[str] = None,
        instance_id: Optional[str] = None
    ) -> str:
        """
        从实例数据中提取instance_name
        
        Args:
            instance_data: 实例数据字典
            display_key: 显示字段名（用于获取instance_name）
            instance_id: 实例ID（如果无法提取名称，使用ID作为名称）
            
        Returns:
            实例名称
        """
        instance_name = None
        
        # 优先使用display_key
        if display_key and display_key in instance_data:
            instance_name = instance_data.get(display_key)
        
        # 如果没有display_key或提取失败，尝试从常见字段获取
        if not instance_name:
            instance_name = instance_data.get("instance_name") or instance_data.get("name")
        
        # 如果还是没有，使用instance_id作为名称
        if not instance_name:
            instance_name = instance_id
        
        return instance_name or "未知实例"
    
    @staticmethod
    def extract_unique_identities(
        instance_data: Dict[str, Any],
        primary_keys: List[str]
    ) -> Dict[str, Any]:
        """
        从实例数据中提取unique_identities（主键字段的值字典）
        
        Args:
            instance_data: 实例数据字典
            primary_keys: 主键字段名列表
            
        Returns:
            主键字段的值字典
        """
        unique_identities = {}
        
        if not primary_keys or not isinstance(primary_keys, list):
            return unique_identities
        
        if not isinstance(instance_data, dict):
            return unique_identities
        
        for pk_field in primary_keys:
            if pk_field in instance_data:
                pk_value = instance_data.get(pk_field)
                if pk_value is not None and pk_value != "":
                    unique_identities[pk_field] = pk_value
        
        return unique_identities
    
    @staticmethod
    def enrich_instance_data(
        instance_data: Dict[str, Any],
        object_type_id: str,
        primary_keys: List[str],
        display_key: Optional[str] = None,
        raise_on_error: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        丰富实例数据，添加instance_id、instance_name和unique_identities
        
        Args:
            instance_data: 实例数据字典（会被修改）
            object_type_id: 对象类型ID
            primary_keys: 主键字段名列表
            display_key: 显示字段名
            raise_on_error: 如果无法提取ID是否抛出异常
            
        Returns:
            丰富后的实例数据，如果无法提取ID返回None
        """
        # 提取instance_id
        instance_id = InstanceUtils.extract_instance_id(
            instance_data, primary_keys, object_type_id, raise_on_error
        )
        
        if not instance_id:
            return None
        
        # 提取instance_name
        instance_name = InstanceUtils.extract_instance_name(
            instance_data, display_key, instance_id
        )
        
        # 提取unique_identities
        unique_identities = InstanceUtils.extract_unique_identities(
            instance_data, primary_keys
        )
        
        # 添加到实例数据中
        instance_data["instance_id"] = instance_id
        instance_data["instance_name"] = instance_name
        instance_data["unique_identities"] = unique_identities
        
        return instance_data
    
    @staticmethod
    def extract_instance_id_from_unique_identities(
        unique_identities: Dict[str, Any],
        primary_keys: List[str],
        combine_primary_keys: bool = True
    ) -> Optional[str]:
        """
        从unique_identities中提取instance_id（用于从关系路径API返回的对象中提取）
        
        Args:
            unique_identities: unique_identities字典
            primary_keys: 主键字段名列表
            combine_primary_keys: 是否组合多个主键（True：组合所有非空主键，False：只使用第一个主键）
            
        Returns:
            实例ID，如果无法提取返回None
        """
        if not unique_identities:
            return None
        
        # 方案：组合所有非空的主键字段（更准确，支持复合主键）
        if combine_primary_keys and primary_keys:
            pk_values = []
            for pk_field in primary_keys:
                if pk_field in unique_identities:
                    pk_value = unique_identities.get(pk_field)
                    # 只包含非空值
                    if pk_value is not None and pk_value != "":
                        pk_values.append(str(pk_value))
            
            if pk_values:
                instance_id = ",".join(pk_values)
                return instance_id
        
        # 兼容旧逻辑：如果schema中有primary_keys信息，优先按顺序查找第一个
        if primary_keys:
            for pk_field in primary_keys:
                if pk_field in unique_identities and unique_identities.get(pk_field):
                    return unique_identities.get(pk_field)
        
        # 如果按primary_keys找不到，则查找unique_identities中的第一个非空值
        for key, value in unique_identities.items():
            if value:
                return value
        
        return None
    
    @staticmethod
    def build_primary_key_condition(
        instance_id: str,
        primary_keys: List[str]
    ) -> Optional[Dict[str, Any]]:
        """
        根据instance_id和primary_keys构建主键查询条件
        
        支持单个主键和组合主键：
        - 单个主键：instance_id是单个值，primary_keys只有一个字段
        - 组合主键：instance_id是用逗号分隔的值，primary_keys有多个字段
        
        Args:
            instance_id: 实例ID（可能是单个值或逗号分隔的组合值）
            primary_keys: 主键字段名列表
            
        Returns:
            查询条件字典，格式：
            {
                "operation": "and" 或 "or",
                "sub_conditions": [
                    {
                        "field": "字段名",
                        "operation": "==",
                        "value": "值",
                        "value_from": "const"
                    }
                ]
            }
            如果无法构建条件，返回None
        """
        if not instance_id or not primary_keys or not isinstance(primary_keys, list):
            logger.warning(
                f"无法构建主键查询条件: instance_id={instance_id}, primary_keys={primary_keys}"
            )
            return None
        
        instance_id = str(instance_id).strip()
        if not instance_id:
            return None
        
        # 判断是否为组合主键（用逗号分隔）
        pk_values = [v.strip() for v in instance_id.split(",") if v.strip()]
        
        if not pk_values:
            return None
        
        # 情况1：单个主键
        if len(primary_keys) == 1:
            # 即使instance_id包含逗号，也当作单个值处理（可能是字段值本身包含逗号）
            return {
                "operation": "or",
                "sub_conditions": [
                    {
                        "field": primary_keys[0],
                        "operation": "==",
                        "value": instance_id,
                        "value_from": "const"
                    }
                ]
            }
        
        # 情况2：组合主键（多个主键字段）
        if len(pk_values) == len(primary_keys):
            # instance_id的值数量与primary_keys数量匹配，构建组合条件
            sub_conditions = []
            for pk_field, pk_value in zip(primary_keys, pk_values):
                sub_conditions.append({
                    "field": pk_field,
                    "operation": "==",
                    "value": pk_value,
                    "value_from": "const"
                })
            
            # 组合主键需要用"and"连接（所有条件都满足）
            return {
                "operation": "and",
                "sub_conditions": sub_conditions
            }
        elif len(pk_values) == 1:
            # instance_id只有一个值，但primary_keys有多个字段
            # 这种情况可能是部分主键匹配，只使用第一个主键字段
            logger.debug(
                f"instance_id只有一个值但primary_keys有多个字段，"
                f"使用第一个主键字段: {primary_keys[0]}"
            )
            return {
                "operation": "or",
                "sub_conditions": [
                    {
                        "field": primary_keys[0],
                        "operation": "==",
                        "value": pk_values[0],
                        "value_from": "const"
                    }
                ]
            }
        else:
            # instance_id的值数量与primary_keys数量不匹配，无法构建准确条件
            logger.warning(
                f"instance_id的值数量({len(pk_values)})与primary_keys数量({len(primary_keys)})不匹配，"
                f"无法构建准确的主键查询条件: instance_id={instance_id}, primary_keys={primary_keys}"
            )
            # 尝试使用前N个字段匹配前N个值
            min_count = min(len(pk_values), len(primary_keys))
            sub_conditions = []
            for i in range(min_count):
                sub_conditions.append({
                    "field": primary_keys[i],
                    "operation": "==",
                    "value": pk_values[i],
                    "value_from": "const"
                })
            
            if sub_conditions:
                return {
                    "operation": "and",
                    "sub_conditions": sub_conditions
                }
            
            return None

