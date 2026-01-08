# -*- coding: utf-8 -*-
"""
重排序工具模块
提供条件召回和语义实例召回共用的重排序方法
"""

import time
from typing import List, Dict, Any, Optional
from data_retrieval.logs.logger import logger
from data_retrieval.tools.graph_tools.driven.external.rerank_client import RerankClient
from ...infra.utils.instance_utils import InstanceUtils
from ...infra.utils.instance_text_builder import UNIFIED_INSTANCE_TEXT_OPTIONS, build_instance_text


async def rerank_instances(
    instances: List[Dict[str, Any]],
    query: str,
    object_type_id: str,
    schema_info: Dict[str, Any],
    top_k: int = 10,
    build_description_func: callable = None,
    verbose_logging: bool = False,
    enable_rerank: bool = True
) -> List[Dict[str, Any]]:
    """
    使用向量重排序对实例进行过滤（公共方法）
    
    Args:
        instances: 实例列表
        query: 完整查询问题
        object_type_id: 对象类型ID
        schema_info: schema信息
        top_k: 返回Top-K个实例
        build_description_func: 构建实例描述的函数，如果为None则使用默认方法
        verbose_logging: 是否输出详细日志（条件召回使用详细日志，语义召回使用简单日志）
        
    Returns:
        过滤后的实例列表
    """
    if not query or not instances:
        return instances[:top_k]
    
    # 如果禁用重排序，使用启发式分数
    if not enable_rerank:
        logger.info(f"[向量重排序] rerank_instances：enable_rerank=False，跳过向量重排序，使用启发式分数降级策略，实例数量={len(instances)}")
        q = (query or "").strip().lower()

        def _pick_name(inst: Dict[str, Any]) -> str:
            for k in ("instance_name", "name"):
                v = inst.get(k)
                if isinstance(v, str) and v.strip():
                    return v.strip()
            # 尝试 *_name 字段兜底
            for k, v in (inst or {}).items():
                if isinstance(k, str) and k.endswith("_name") and isinstance(v, str) and v.strip():
                    return v.strip()
            return ""

        scored = []
        for inst in instances:
            inst2 = inst.copy() if isinstance(inst, dict) else {}
            name = _pick_name(inst2).lower()
            # 启发式：完全相等 > 包含 > 否则 0
            if q and name == q:
                inst2["relevance_score"] = 1.0
            elif q and name and q in name:
                inst2["relevance_score"] = 0.8
            else:
                inst2["relevance_score"] = 0.0
            try:
                score = float(inst2.get("relevance_score") or 0.0)
            except Exception:
                score = 0.0
            scored.append((score, inst2))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [inst for _, inst in scored[:top_k]]
    
    # 注意：即使 instances 数量 <= top_k，也应尽量给出可比较的分数，
    # 否则下游跨对象类型排序时会把这类实例当成 0 分，导致"完全匹配"也排不靠前。
    # 这里提供一个轻量兜底：为缺少 relevance_score 的实例计算启发式分数（不额外调用 rerank 服务）。
    if len(instances) <= top_k:
        q = (query or "").strip().lower()

        def _pick_name(inst: Dict[str, Any]) -> str:
            for k in ("instance_name", "name"):
                v = inst.get(k)
                if isinstance(v, str) and v.strip():
                    return v.strip()
            # 尝试 *_name 字段兜底
            for k, v in (inst or {}).items():
                if isinstance(k, str) and k.endswith("_name") and isinstance(v, str) and v.strip():
                    return v.strip()
            return ""

        scored = []
        for inst in instances:
            inst2 = inst.copy() if isinstance(inst, dict) else {}
            if "relevance_score" not in inst2 or inst2.get("relevance_score") is None:
                name = _pick_name(inst2).lower()
                # 启发式：完全相等 > 包含 > 否则 0
                if q and name == q:
                    inst2["relevance_score"] = 1.0
                elif q and name and q in name:
                    inst2["relevance_score"] = 0.8
                else:
                    inst2["relevance_score"] = 0.0
            try:
                score = float(inst2.get("relevance_score") or 0.0)
            except Exception:
                score = 0.0
            scored.append((score, inst2))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [inst for _, inst in scored[:top_k]]
    
    try:
        # 构建实例描述文本列表
        instance_texts = []
        for instance in instances:
            if build_description_func:
                description = build_description_func(instance, object_type_id, schema_info)
            else:
                description = build_instance_description(instance, object_type_id, schema_info)
            instance_texts.append(description)
        
        if verbose_logging:
            logger.info("=" * 80)
            logger.info(f"实例向量重排序 - 查询问题: {query}")
            logger.info(f"共 {len(instance_texts)} 个实例需要重排序:")
            logger.info("-" * 80)
            for idx, text in enumerate(instance_texts, 1):
                instance_id = instances[idx-1].get("instance_id", "unknown")
                logger.info(f"[{idx}] 实例ID: {instance_id}")
                logger.info(f"     描述文本: {text}")
            logger.info("=" * 80)
        else:
            logger.info(f"[向量重排序] rerank_instances：enable_rerank=True，开始对 {len(instances)} 个实例进行向量重排序，查询: {query}")
        
        # 使用RerankClient进行向量重排序
        logger.debug(f"[向量重排序] 调用RerankClient.ado_rerank进行实例重排序，实例数量={len(instance_texts)}")
        rerank_client = RerankClient()
        t0 = time.monotonic()
        try:
            rerank_scores = await rerank_client.ado_rerank(instance_texts, query)
            logger.debug(f"[向量重排序] RerankClient.ado_rerank返回，分数数量={len(rerank_scores) if rerank_scores else 0}")
        finally:
            elapsed_ms = (time.monotonic() - t0) * 1000
            try:
                from ...infra.utils.timing_utils import add_cost
                add_cost("rerank", elapsed_ms)
            except Exception:
                pass
        
        # 处理重排序结果
        if rerank_scores and len(rerank_scores) > 0:
            # 新格式: [{"relevance_score": 0.985, "index": 1, "document": null}, ...]
            sorted_scores = sorted(rerank_scores, key=lambda x: x.get("index", 0))
            validated_scores = [
                float(item.get("relevance_score")) 
                for item in sorted_scores 
                if isinstance(item.get("relevance_score"), (int, float))
            ]
            
            # 将实例和分数配对
            scored_instances = []
            for i, score in enumerate(validated_scores):
                if i < len(instances):
                    instance_with_score = instances[i].copy()
                    instance_with_score["relevance_score"] = score
                    scored_instances.append((score, instance_with_score))
            
            # 按分数降序排序
            scored_instances.sort(key=lambda x: x[0], reverse=True)
            
            # 返回Top-K个实例
            filtered_instances = [inst for _, inst in scored_instances[:top_k]]
            
            logger.info(f"实例向量重排序完成，原始数量: {len(instances)}, 过滤后数量: {len(filtered_instances)}")
            return filtered_instances
        else:
            logger.warning("向量重排序服务未返回分数，使用启发式分数降级策略")
            # 降级策略：使用启发式分数
            q = (query or "").strip().lower()
            def _pick_name(inst: Dict[str, Any]) -> str:
                for k in ("instance_name", "name"):
                    v = inst.get(k)
                    if isinstance(v, str) and v.strip():
                        return v.strip()
                for k, v in (inst or {}).items():
                    if isinstance(k, str) and k.endswith("_name") and isinstance(v, str) and v.strip():
                        return v.strip()
                return ""
            scored = []
            for inst in instances:
                inst2 = inst.copy() if isinstance(inst, dict) else {}
                name = _pick_name(inst2).lower()
                if q and name == q:
                    inst2["relevance_score"] = 1.0
                elif q and name and q in name:
                    inst2["relevance_score"] = 0.8
                else:
                    inst2["relevance_score"] = 0.0
                try:
                    score = float(inst2.get("relevance_score") or 0.0)
                except Exception:
                    score = 0.0
                scored.append((score, inst2))
            scored.sort(key=lambda x: x[0], reverse=True)
            return [inst for _, inst in scored[:top_k]]
            
    except Exception as e:
        logger.warning(f"实例向量重排序失败: {str(e)}，使用启发式分数降级策略", exc_info=True)
        # 降级策略：使用启发式分数
        q = (query or "").strip().lower()
        def _pick_name(inst: Dict[str, Any]) -> str:
            for k in ("instance_name", "name"):
                v = inst.get(k)
                if isinstance(v, str) and v.strip():
                    return v.strip()
            for k, v in (inst or {}).items():
                if isinstance(k, str) and k.endswith("_name") and isinstance(v, str) and v.strip():
                    return v.strip()
            return ""
        scored = []
        for inst in instances:
            inst2 = inst.copy() if isinstance(inst, dict) else {}
            name = _pick_name(inst2).lower()
            if q and name == q:
                inst2["relevance_score"] = 1.0
            elif q and name and q in name:
                inst2["relevance_score"] = 0.8
            else:
                inst2["relevance_score"] = 0.0
            try:
                score = float(inst2.get("relevance_score") or 0.0)
            except Exception:
                score = 0.0
            scored.append((score, inst2))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [inst for _, inst in scored[:top_k]]


def extract_instance_id_from_obj(
    obj: Dict[str, Any],
    obj_type_id: str,
    schema_map: Dict[str, Dict[str, Any]]
) -> Optional[str]:
    """
    从对象中提取instance_id（公共方法）
    
    Args:
        obj: 对象字典（包含unique_identities字段）
        obj_type_id: 对象类型ID
        schema_map: schema映射，格式为 {object_type_id: {primary_keys: [...], ...}}
        
    Returns:
        实例ID，如果无法提取返回None
    """
    unique_identities = obj.get("unique_identities", {})
    if not unique_identities:
        return None
    
    obj_schema = schema_map.get(obj_type_id, {})
    primary_keys = obj_schema.get("primary_keys", [])
    
    # 使用公共工具类提取instance_id
    return InstanceUtils.extract_instance_id_from_unique_identities(
        unique_identities, primary_keys
    )


def build_instance_description(
    instance: Dict[str, Any],
    object_type_id: str,
    schema_info: Dict[str, Any]
) -> str:
    """
    构建实例描述文本，用于向量重排序（统一版本）
    
    规则：
    1. 优先使用instance_name（如果已存在）
    2. 如果没有instance_name，尝试从properties中提取（使用display_key或primary_keys）
    3. 如果还是没有，使用object_type_name + instance_id
    4. 添加所有字符串类型属性（排除非字符串类型和空字符串）
    
    Args:
        instance: 实例信息字典（可能包含properties字段，也可能properties就是instance本身）
        object_type_id: 对象类型ID
        schema_info: schema信息
        
    Returns:
        实例描述文本
    """
    return build_instance_text(
        instance,
        object_type_id=object_type_id,
        schema_info=schema_info,
        options=UNIFIED_INSTANCE_TEXT_OPTIONS,
    )



