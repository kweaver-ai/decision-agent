# -*- coding: utf-8 -*-
"""
语义实例召回模块
实现基于语义检索（match/knn）的实例数据召回，包括评分、过滤和关联判定功能
"""

import asyncio
import math
import time
import re
from typing import List, Dict, Any, Optional, Set, Tuple, Callable
from collections import defaultdict
from data_retrieval.logs.logger import logger
from data_retrieval.tools.graph_tools.driven.external.rerank_client import RerankClient
from ...config import config
from ...core.scoring.instance_scorer import InstanceScorer
from ...models import SemanticInstanceRetrievalConfig
from ...infra.utils.instance_utils import InstanceUtils
from ...infra.utils.ranking_utils import UnifiedRankingUtils, RankingStrategy
from ...services.semantic.object_api import call_object_retrieval_api
from ...services.semantic.instances import retrieve_map_for_all_object_types

# 知识网络查询API基础URL
KNOWLEDGE_NETWORK_QUERY_API_BASE = config.KNOWLEDGE_NETWORK_QUERY_API_BASE


class SemanticInstanceRetrieval:
    """语义实例召回类"""

    @staticmethod
    def _split_query_terms(query: Any) -> List[str]:
        """
        将 query 拆分为“关键词/短语”列表，用于多关键词覆盖、直接命中判定等。

        规则：
        - 使用空白符与常见分隔符（逗号/分号/斜杠/竖线）切分
        - 全部转小写、去空
        """
        if not isinstance(query, str):
            return []
        q = (query or "").strip().lower()
        if not q:
            return []
        parts = re.split(r"[\s,，;；/|]+", q)
        return [p for p in (pp.strip() for pp in parts) if p]

    @classmethod
    def _is_text_field(cls, field_info: Dict[str, Any]) -> bool:
        """
        判断属性是否为文本类型（text/string），只有文本类型属性才应该用于语义检索条件匹配
        
        Args:
            field_info: 属性信息字典，包含data_type字段
            
        Returns:
            如果属性是text/string类型返回True，否则返回False
        """
        if not isinstance(field_info, dict):
            return False
        
        data_type = field_info.get("data_type") or field_info.get("type") or ""
        if not isinstance(data_type, str):
            return False
        
        # 转换为小写进行比较
        data_type_lower = data_type.lower().strip()
        
        # 文本类型：text, string, varchar, char, text[], string[]等
        text_types = {"text", "string", "varchar", "char"}
        
        # 检查是否匹配文本类型（支持数组类型，如text[]）
        for text_type in text_types:
            if data_type_lower == text_type or data_type_lower.startswith(text_type + "["):
                return True
        
        return False

    @classmethod
    def _estimate_field_keep_k(
        cls,
        total_fields: int,
        semantic_config: SemanticInstanceRetrievalConfig,
    ) -> int:
        """
        估算属性预算截断后会保留的属性数 k（不依赖语义分数）。
        与 `_apply_field_budget` 的 k 计算保持一致，用于决定是否有必要调用 rerank 进行属性打分。
        """
        if not isinstance(total_fields, int) or total_fields <= 0:
            return 0

        ratio = float(getattr(semantic_config, "semantic_field_keep_ratio", 0.2) or 0.2)
        keep_min = int(getattr(semantic_config, "semantic_field_keep_min", 5) or 5)
        keep_max = int(getattr(semantic_config, "semantic_field_keep_max", 15) or 15)
        max_sub = int(getattr(semantic_config, "max_semantic_sub_conditions", 10) or 10)

        k = int(math.ceil(total_fields * ratio))
        k = max(k, keep_min)
        k = min(k, keep_max, total_fields)
        k = min(k, max_sub)
        return max(k, 0)

    @classmethod
    def _estimate_desired_sub_conditions(
        cls,
        fields: List[Dict[str, Any]],
    ) -> int:
        """
        在 `max_sub_conditions` 不设限时，`_build_semantic_query_conditions` 理论上最多会为每个属性追加：
        - knn（若支持）
        - ==（若支持）
        - match（若支持）
        因此这里用三类条件的数量之和，估算"理想情况下会添加多少条 sub_conditions"。
        当 max_sub_conditions >= 该值时，属性顺序不会影响最终 sub_conditions 集合，可跳过属性 rerank。
        """
        if not fields:
            return 0
        knn_count = sum(1 for f in fields if f.get("has_knn"))
        exact_count = sum(1 for f in fields if f.get("has_exact_match"))
        match_count = sum(1 for f in fields if f.get("has_match"))
        return int(knn_count + exact_count + match_count)

    @classmethod
    async def _global_rerank_and_trim_instance_map(
        cls,
        *,
        instance_map: Dict[str, List[Dict[str, Any]]],
        query: str,
        schema_info: Dict[str, Any],
        per_type_top_k: int,
        semantic_config: Optional[SemanticInstanceRetrievalConfig] = None,
        enable_rerank: bool = True,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        全局一次实例重排序：
        - 将所有对象类型候选实例扁平化后统一调用 rerank（内部按 batch_size 分批，避免请求体过大）
        - 将 relevance_score/final_score 回填到实例上
        - 再按对象类型分别截断到 per_type_top_k

        设计目的：
        - 减少“每对象类型一次 rerank”的调用次数
        - 保持每个对象类型仍能返回一定数量的实例（不改变 per-type 截断语义）
        - 为后续跨对象类型综合平衡（semantic_output）提供可比较的基础分
        """
        if not instance_map or not isinstance(instance_map, dict):
            return {}
        if not query:
            # 无 query 时无法比较，直接按原顺序 per-type 截断
            return {
                obj_id: (insts[:per_type_top_k] if isinstance(insts, list) else [])
                for obj_id, insts in instance_map.items()
            }
        if not semantic_config:
            semantic_config = SemanticInstanceRetrievalConfig()

        # 兜底：非法 top_k
        try:
            per_type_top_k = int(per_type_top_k)
        except Exception:
            per_type_top_k = 10
        if per_type_top_k <= 0:
            per_type_top_k = 1

        # 扁平化：记录 (obj_id, inst_idx) -> instance
        flat: List[Tuple[str, int, Dict[str, Any]]] = []
        texts: List[str] = []
        for obj_id, insts in (instance_map or {}).items():
            if not isinstance(insts, list) or not obj_id:
                continue
            for idx, inst in enumerate(insts):
                if not isinstance(inst, dict):
                    continue
                flat.append((obj_id, idx, inst))
                try:
                    # 复用统一实例描述（内部已统一为 structured 文本）
                    desc = cls._build_instance_description(inst, obj_id, schema_info)
                except Exception:
                    desc = ""
                texts.append(desc or "")

        if not flat:
            return {obj_id: [] for obj_id in (instance_map or {}).keys()}

        # 如果总数很小且所有类型都 <= top_k，历史上会“完全不调用 rerank 服务”；
        # 这里保持省调用：直接走 per-type 兜底打分（不额外调用 rerank 服务）。
        if all(isinstance(v, list) and len(v) <= per_type_top_k for v in instance_map.values()):
            from ...core.rerank.rerank_utils import rerank_instances as _rerank_instances_fallback
            trimmed: Dict[str, List[Dict[str, Any]]] = {}
            for obj_id, insts in instance_map.items():
                if not isinstance(insts, list) or not insts:
                    trimmed[obj_id] = []
                    continue
                trimmed[obj_id] = await _rerank_instances_fallback(
                    instances=insts,
                    query=query,
                    object_type_id=obj_id,
                    schema_info=schema_info,
                    top_k=per_type_top_k,
                    build_description_func=cls._build_instance_description,
                    verbose_logging=False,
                    enable_rerank=enable_rerank,
                )
                # fallback 会写 relevance_score；补一个 final_score 供下游统一使用
                for it in trimmed[obj_id]:
                    if isinstance(it, dict) and it.get("final_score") is None and it.get("relevance_score") is not None:
                        try:
                            it["final_score"] = float(it.get("relevance_score") or 0.0)
                        except Exception:
                            pass
            return trimmed

        # 全局调用 rerank（按 batch 分批）
        batch_size = int(getattr(semantic_config, "semantic_field_rerank_batch_size", 128) or 128)
        # 优先使用参数传入的enable_rerank（这是从用户配置直接传递下来的），而不是从semantic_config中获取
        # semantic_config.enable_rerank 的值可能不是最新的用户配置
        logger.info(f"[向量重排序] 全局实例重排序：enable_rerank={enable_rerank}（使用参数传入的值），实例数量={len(flat)}，batch_size={batch_size}")
        
        # 当 enable_rerank=False 时，优先使用实例的原始_score分数
        if not enable_rerank:
            scores = []
            original_score_count = 0
            keyword_score_count = 0
            
            for (obj_id, _, inst) in flat:
                # 优先使用API返回的原始_score字段（knn/match分数）
                original_score = None
                if "_score" in inst and inst["_score"] is not None:
                    try:
                        score_val = inst["_score"]
                        # 如果是字符串，尝试转换为浮点数
                        if isinstance(score_val, str):
                            score_val = float(score_val)
                        original_score = float(score_val)
                    except (ValueError, TypeError):
                        pass
                
                if original_score is not None:
                    # 使用原始_score分数（API返回的语义检索分数通常比关键词匹配更准确）
                    scores.append(original_score)
                    original_score_count += 1
                else:
                    # 如果没有_score字段，降级到关键词匹配
                    desc = texts[len(scores)] if len(scores) < len(texts) else ""
                    keyword_score = UnifiedRankingUtils.compute_keyword_match_score(desc, query)
                    scores.append(keyword_score)
                    keyword_score_count += 1
            
            logger.info(f"[向量重排序] enable_rerank=False，使用原始_score分数：{original_score_count}个，降级到关键词匹配：{keyword_score_count}个")
        else:
            # enable_rerank=True 时，使用向量重排序
            scores = await cls._rerank_texts(query=query, texts=texts, batch_size=batch_size, enable_rerank=enable_rerank)
            if len(scores) != len(flat):
                # 强制对齐（理论上 _rerank_texts 已保证长度一致）
                if len(scores) < len(flat):
                    scores.extend([0.0 for _ in range(len(flat) - len(scores))])
                else:
                    scores = scores[: len(flat)]

        # 回填并按类型分桶
        per_type_scored: Dict[str, List[Tuple[float, Dict[str, Any]]]] = {}
        for (obj_id, _, inst), sc in zip(flat, scores):
            try:
                score_f = float(sc) if isinstance(sc, (int, float)) else 0.0
            except Exception:
                score_f = 0.0
            inst_copy = inst.copy()
            inst_copy["relevance_score"] = score_f
            # 统一挂载 final_score，便于后续跨类型综合排序
            inst_copy["final_score"] = score_f
            # 保留原始_score字段（如果存在），用于日志输出
            if "_score" not in inst_copy and "_score" in inst:
                inst_copy["_score"] = inst["_score"]
            per_type_scored.setdefault(obj_id, []).append((score_f, inst_copy))
        
        # 打印每个实例的原始_score分数（enable_rerank=False时，用于确认API返回的排序）
        if not enable_rerank:
            logger.info(f"[向量重排序] API返回的原始_score分数详情（共{len(flat)}个实例，按对象类型分组，排序前顺序）：")
            for obj_id, pairs in per_type_scored.items():
                if not pairs:
                    continue
                logger.info(f"  [对象类型: {obj_id}]（共{len(pairs)}个实例）：")
                for idx, (score, inst) in enumerate(pairs[:20], 1):  # 只打印前20个
                    # 获取实例名称
                    inst_name_raw = inst.get("instance_name") or inst.get("name") or ""
                    inst_name = str(inst_name_raw) if inst_name_raw else ""
                    if not inst_name:
                        for key in inst.keys():
                            if key.endswith("_name") and isinstance(inst[key], str):
                                inst_name = inst[key]
                                break
                    # 获取原始_score字段（如果存在）
                    original_score = inst.get("_score", "N/A")
                    logger.info(f"    [{idx}] {inst_name[:50] if inst_name else 'N/A'}: relevance_score={score}, 原始_score字段={original_score}")
                if len(pairs) > 20:
                    logger.info(f"    ... (还有{len(pairs) - 20}个实例未显示)")

        # 每类型排序截断
        trimmed_map: Dict[str, List[Dict[str, Any]]] = {}
        for obj_id, pairs in per_type_scored.items():
            pairs.sort(key=lambda x: x[0], reverse=True)
            
            # 打印排序后的分数（仅当enable_rerank=False时，用于确认排序结果）
            if not enable_rerank and pairs:
                logger.info(f"[向量重排序] 对象类型 {obj_id} 排序后（保留前{min(len(pairs), per_type_top_k)}个，按分数降序）：")
                for idx, (score, inst) in enumerate(pairs[:per_type_top_k], 1):
                    # 获取实例名称
                    inst_name_raw = inst.get("instance_name") or inst.get("name") or ""
                    inst_name = str(inst_name_raw) if inst_name_raw else ""
                    if not inst_name:
                        for key in inst.keys():
                            if key.endswith("_name") and isinstance(inst[key], str):
                                inst_name = inst[key]
                                break
                    logger.info(f"    [{idx}] {inst_name[:50] if inst_name else 'N/A'}: relevance_score={score}")
            
            trimmed_map[obj_id] = [it for _, it in pairs[:per_type_top_k]]

        # 对于输入里存在但没有有效 dict 实例的类型，仍返回空列表（保持结构）
        for obj_id in instance_map.keys():
            trimmed_map.setdefault(obj_id, [])

        logger.info(
            f"全局实例rerank完成：types={len(trimmed_map)}, total_instances={len(flat)}, "
            f"per_type_top_k={per_type_top_k}, batch_size={batch_size}"
        )
        return trimmed_map

    @classmethod
    def _build_semantic_query_conditions_multi_keyword(
        cls,
        *,
        full_query: str,
        keywords: List[str],
        searchable_fields: List[Dict[str, Any]],
        candidate_limit: int,
        max_sub_conditions: int,
        knn_limit_key: str = "k",
        knn_limit_value: Any = 10,
        include_exact_match: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """
        构建“多关键词合并”的语义检索查询条件：
        - 目标：用一次 object_query 覆盖多个关键词的召回意图，减少请求次数
        - 策略：按"预算"分配 sub_conditions（不做属性数量硬限制）：
          1) 先尽可能对所有候选属性各加一条 knn(full_query)（覆盖面优先）
          2) 若还有预算，再对支持 match 的属性追加 match（对每个属性遍历 keywords）
          3) 可选：再追加 '==' 精确匹配（默认关闭）
        - 约束：严格受 max_sub_conditions 截断，避免请求体膨胀/超限

        说明：
        - keywords 为空时退化为 full_query 单关键词
        - 默认不包含 '=='，因为在多关键词场景下它更容易造成 sub_conditions 爆炸且收益不稳定
        """
        if not searchable_fields:
            return None
        if not full_query:
            return None

        # 规范化关键词：去空、去重（保持顺序），并确保至少包含 full_query
        norm_keywords: List[str] = []
        seen = set()
        for kw in (keywords or []):
            kw = (kw or "").strip()
            if not kw or kw in seen:
                continue
            seen.add(kw)
            norm_keywords.append(kw)
        if full_query not in seen:
            norm_keywords.insert(0, full_query)

        max_sub = int(max_sub_conditions) if isinstance(max_sub_conditions, int) else 10
        max_sub = max(max_sub, 1)

        sub_conditions: List[Dict[str, Any]] = []

        def _add_condition(field_name: str, op: str, value: str, extra: Optional[Dict[str, Any]] = None) -> None:
            if len(sub_conditions) >= max_sub:
                return
            cond: Dict[str, Any] = {"field": field_name, "operation": op, "value": value}
            if extra:
                cond.update(extra)
            sub_conditions.append(cond)

        # 1) knn：优先覆盖所有候选属性（每属性最多加1条），直到预算耗尽
        # 只对text/string类型的属性添加条件，其他类型（如int）不应该进行条件匹配
        for field_info in searchable_fields:
            if len(sub_conditions) >= max_sub:
                break
            field_name = field_info.get("name")
            supported_ops = field_info.get("condition_operations", []) or []
            if not field_name:
                continue
            # 只对文本类型属性进行条件匹配
            if not cls._is_text_field(field_info):
                continue
            if field_info.get("has_knn") and "knn" in supported_ops:
                _add_condition(
                    field_name=field_name,
                    op="knn",
                    value=full_query,
                    extra={"limit_key": knn_limit_key, "limit_value": str(knn_limit_value)},
                )

        # 2) match：用关键词扩召回，直到预算耗尽（不再做属性数硬限制）
        # 只对text/string类型的属性添加条件，其他类型（如int）不应该进行条件匹配
        for field_info in searchable_fields:
            if len(sub_conditions) >= max_sub:
                break
            field_name = field_info.get("name")
            supported_ops = field_info.get("condition_operations", []) or []
            if not field_name:
                continue
            # 只对文本类型属性进行条件匹配
            if not cls._is_text_field(field_info):
                continue
            if not field_info.get("has_match"):
                continue
            preferred_match_op = field_info.get("preferred_match_op")
            if not preferred_match_op or preferred_match_op not in supported_ops:
                continue
            for kw in norm_keywords:
                if len(sub_conditions) >= max_sub:
                    break
                _add_condition(field_name=field_name, op=preferred_match_op, value=kw)

        # 3) 可选：精确匹配（==）——默认关闭（多关键词场景常导致 sub_conditions 过多）
        # 只对text/string类型的属性添加条件，其他类型（如int）不应该进行条件匹配
        if include_exact_match:
            for field_info in searchable_fields:
                if len(sub_conditions) >= max_sub:
                    break
                field_name = field_info.get("name")
                supported_ops = field_info.get("condition_operations", []) or []
                if not field_name:
                    continue
                # 只对文本类型属性进行条件匹配
                if not cls._is_text_field(field_info):
                    continue
                if field_info.get("has_exact_match") and "==" in supported_ops:
                    for kw in norm_keywords:
                        if len(sub_conditions) >= max_sub:
                            break
                        _add_condition(field_name=field_name, op="==", value=kw)

        if not sub_conditions:
            return None

        return {
            "condition": {"operation": "or", "sub_conditions": sub_conditions},
            "need_total": True,
            "limit": candidate_limit,
        }

    @classmethod
    def _get_mandatory_semantic_field_names_from_schema(
        cls,
        *,
        schema_info: Dict[str, Any],
        object_type_id: str,
    ) -> List[str]:
        """
        从 schema_info 提取该对象类型"必须优先参与语义召回"的属性名：
        - display_key（通常是名称属性，如 disease_name / drug_name）
        - primary_keys（主键属性，便于精确定位/去重）
        
        背景：多关键词候选召回的属性选择会按语义分数截断，并且 match/knn 进一步限制属性数，
        如果 display_key 被截掉，就可能出现“实体名在 query 里，但候选召回完全拉不到该实体”的漏召回。
        """
        if not schema_info or not object_type_id:
            return []

        obj_types = (schema_info or {}).get("object_types", []) or []
        for ot in obj_types:
            ot_id = ot.get("concept_id") or ot.get("id")
            if ot_id != object_type_id:
                continue
            display_key = (ot.get("display_key") or "").strip()
            primary_keys = ot.get("primary_keys", []) or []
            names: List[str] = []
            if display_key:
                names.append(display_key)
            for pk in primary_keys:
                if pk and pk not in names:
                    names.append(pk)
            return names
        return []

    @classmethod
    def _ensure_mandatory_fields_first(
        cls,
        *,
        selected_fields: List[Dict[str, Any]],
        searchable_fields: List[Dict[str, Any]],
        mandatory_field_names: List[str],
    ) -> List[Dict[str, Any]]:
        """
        保障 mandatory_field_names 在 selected_fields 中存在且排在前面（优先占用 match/knn 的属性预算）。
        """
        if not searchable_fields:
            return selected_fields or []
        if not mandatory_field_names:
            return selected_fields or []

        # name -> field_info（来自 searchable_fields，保证结构完整）
        searchable_map = {
            (f.get("name") or ""): f for f in searchable_fields if isinstance(f, dict) and f.get("name")
        }

        # 先按 schema 给的顺序把 mandatory 属性拼出来（不存在于 searchable_fields 的就跳过）
        mandatory_fields: List[Dict[str, Any]] = []
        for fname in mandatory_field_names:
            f = searchable_map.get(fname)
            if f and f not in mandatory_fields:
                mandatory_fields.append(f)

        if not mandatory_fields:
            return selected_fields or []

        # 再拼接原有 selected_fields（去重）
        out: List[Dict[str, Any]] = []
        seen_names = set()
        for f in mandatory_fields + (selected_fields or []):
            if not isinstance(f, dict):
                continue
            name = f.get("name")
            if not name or name in seen_names:
                continue
            seen_names.add(name)
            out.append(f)
        return out

    @classmethod
    async def semantic_retrieve_candidate_instances_multi_keyword(
        cls,
        *,
        full_query: str,
        keywords: List[str],
        object_type: Dict[str, Any],
        kn_id: str,
        schema_info: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
        candidate_limit: int = 50,
        timeout: float = 5.0,
        semantic_config: Optional[SemanticInstanceRetrievalConfig] = None,
        selected_fields: Optional[List[Dict[str, Any]]] = None,
        knn_limit_value: Any = 10,
        include_exact_match: bool = False,
        enable_rerank: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        对单个对象类型进行“多关键词合并”的候选实例召回（不做rerank、不做过滤）。
        """
        object_type_id = object_type.get("concept_id") or object_type.get("id")
        if not object_type_id:
            logger.warning("对象类型信息中没有找到ID，跳过候选实例召回")
            return []

        searchable_fields = cls._find_semantic_searchable_fields(object_type, max_fields=None)
        if not searchable_fields:
            logger.info(f"对象类型 {object_type_id} 没有支持语义检索的属性，跳过候选实例召回")
            return []

        if not semantic_config:
            semantic_config = SemanticInstanceRetrievalConfig()

        if selected_fields is None:
            # enable_rerank 参数已从函数参数传入，不再从 semantic_config 中读取
            selected_fields = await cls._select_fields_by_semantic_score(
                query=full_query,
                object_type=object_type,
                searchable_fields=searchable_fields,
                semantic_config=semantic_config,
                enable_rerank=enable_rerank,
            )

        # 重要：强制把 display_key / primary_keys 放回属性列表最前面，避免"实体名在 query 中但候选召回拉不到"的漏召回
        mandatory_names = cls._get_mandatory_semantic_field_names_from_schema(
            schema_info=schema_info or {},
            object_type_id=object_type_id,
        )
        selected_fields = cls._ensure_mandatory_fields_first(
            selected_fields=selected_fields or [],
            searchable_fields=searchable_fields,
            mandatory_field_names=mandatory_names,
        )

        query_condition = cls._build_semantic_query_conditions_multi_keyword(
            full_query=full_query,
            keywords=keywords,
            searchable_fields=selected_fields,
            candidate_limit=candidate_limit,
            max_sub_conditions=int(getattr(semantic_config, "max_semantic_sub_conditions", 10) or 10),
            knn_limit_key="k",
            knn_limit_value=knn_limit_value,
            include_exact_match=include_exact_match,
        )
        if not query_condition:
            logger.warning(f"无法为对象类型 {object_type_id} 构建多关键词候选召回查询条件")
            return []

        api_result = await cls._call_object_retrieval_api(
            kn_id=kn_id,
            object_type_id=object_type_id,
            condition=query_condition,
            headers=headers,
            timeout=timeout,
        )
        if not api_result:
            return []

        instances = api_result.get("datas", [])
        if not instances or not isinstance(instances, list):
            return []
        return instances

    @classmethod
    async def semantic_retrieve_candidates_for_all_multi_keyword(
        cls,
        *,
        full_query: str,
        keywords: List[str],
        object_types: List[Dict[str, Any]],
        kn_id: str,
        schema_info: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
        candidate_limit: int = 50,
        max_concurrent: int = 5,
        timeout: float = 5.0,
        semantic_config: Optional[SemanticInstanceRetrievalConfig] = None,
        include_exact_match: bool = False,
        enable_rerank: bool = True,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        多关键词合并候选召回：对所有对象类型各发起一次 object_query。
        目标是把 “关键词数×对象类型数” 的调用次数降到 “对象类型数”。
        """
        if not object_types:
            return {}
        if not semantic_config:
            semantic_config = SemanticInstanceRetrievalConfig()

        # 属性选择：以 full_query 为主（更贴近用户整体意图），并全局复用，避免重复打分
        selected_fields_map: Dict[str, List[Dict[str, Any]]] = await cls._select_fields_for_all_object_types(
            query=full_query, object_types=object_types, semantic_config=semantic_config, enable_rerank=enable_rerank
        )

        async def _retrieve_one(obj_type: Dict[str, Any]) -> List[Dict[str, Any]]:
            obj_id = obj_type.get("concept_id") or obj_type.get("id")
            selected_fields = selected_fields_map.get(obj_id, [])
            return await cls.semantic_retrieve_candidate_instances_multi_keyword(
                full_query=full_query,
                keywords=keywords,
                object_type=obj_type,
                kn_id=kn_id,
                schema_info=schema_info,
                headers=headers,
                candidate_limit=candidate_limit,
                timeout=timeout,
                semantic_config=semantic_config,
                selected_fields=selected_fields,
                include_exact_match=include_exact_match,
                enable_rerank=enable_rerank,  # 传递 enable_rerank 参数
            )

        # 与候选召回旧逻辑一致：不吞异常，任一失败直接抛
        return await retrieve_map_for_all_object_types(
            object_types=object_types,
            retrieve_one=_retrieve_one,
            max_concurrent=max_concurrent,
            log_prefix="候选实例召回(多关键词合并)",
            swallow_exceptions=False,
        )
    
    @classmethod
    def _find_semantic_searchable_fields(
        cls, 
        object_type: Dict[str, Any],
        max_fields: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        找到对象类型中支持语义搜索的属性字段
        
        只选择支持 ==、match、knn 这三个操作符的字段
        对于这些属性，如果同时支持多个操作符，会为每个属性添加所有支持的操作符条件
        
        Args:
            object_type: 对象类型信息
            max_fields: 最多选择的属性数量
            
        Returns:
            属性列表，每个属性包含name和condition_operations信息
        """
        # 统一使用data_properties字段名
        properties = object_type.get("data_properties", [])
        if not isinstance(properties, list):
            properties = []
        
        searchable_fields = []
        
        # 定义语义检索支持的操作符
        semantic_ops = {"==", "match", "knn"}
        
        for prop in properties:
            if not isinstance(prop, dict):
                continue
            
            field_name = prop.get("name") or prop.get("id")
            if not field_name:
                continue
            
            supported_ops = prop.get("condition_operations", [])
            if not isinstance(supported_ops, list):
                continue
            
            # 只选择支持至少一种语义检索操作符（==、match、knn）的属性
            # 排除只支持 !=、not 等其他操作符的属性
            supported_semantic_ops = [op for op in supported_ops if op in semantic_ops]
            if not supported_semantic_ops:
                continue
            
            # 检查支持的具体操作符
            has_exact_match = "==" in supported_ops
            has_match = "match" in supported_ops
            has_knn = "knn" in supported_ops
            
            # 确定match操作符（只支持match）
            preferred_match_op = None
            if "match" in supported_ops:
                preferred_match_op = "match"
            
            field_info = {
                "name": field_name,
                "display_name": prop.get("display_name") or prop.get("name") or prop.get("id") or field_name,
                "comment": prop.get("comment") or prop.get("description") or "",
                "data_type": prop.get("data_type") or prop.get("type") or "",
                "condition_operations": supported_ops,
                "has_exact_match": has_exact_match,
                "has_match": has_match,
                "preferred_match_op": preferred_match_op,
                "has_knn": has_knn
            }
            
            searchable_fields.append(field_info)
        
        # 可选限制：仅用于兜底，正常推荐由"语义打分+比例截断"来控制属性数
        if isinstance(max_fields, int) and max_fields > 0:
            return searchable_fields[:max_fields]
        return searchable_fields

    @classmethod
    def _build_field_rerank_text(cls, object_type: Dict[str, Any], field_info: Dict[str, Any]) -> str:
        """
        构造"属性语义描述文本"，用于 rerank 打分（query 与属性相关性）。
        使用统一的文本构建方法：{对象类型} 的 {属性名称}
        """
        obj_name = object_type.get("concept_name") or object_type.get("name") or object_type.get("id") or ""
        field_name = field_info.get("display_name") or field_info.get("name") or ""
        field_comment = field_info.get("comment", "")
        
        # 使用统一的文本构建方法
        return UnifiedRankingUtils.build_property_text(
            object_name=obj_name,
            property_name=field_name,
            property_comment=field_comment if field_comment else None
        )

    @classmethod
    def _compute_keyword_match_score(cls, text: str, query: str) -> float:
        """
        计算关键词匹配分数（降级策略）
        使用统一的分数计算方法
        """
        return UnifiedRankingUtils.compute_keyword_match_score(text, query)
    
    @classmethod
    async def _rerank_texts(
        cls,
        *,
        query: str,
        texts: List[str],
        batch_size: int = 128,
        rerank_client_factory: Optional[Callable[[], Any]] = None,
        enable_rerank: bool = True,
    ) -> List[float]:
        """
        使用 rerank 服务对 texts 做相关性打分，返回与 texts 同序的分数列表。
        使用统一的排序工具接口
        - enable_rerank=False 时使用关键词匹配降级策略
        - 失败时使用关键词匹配降级策略（保证主流程可降级，不影响召回可用性）
        """
        if not texts:
            return []
        if not query:
            return [0.0 for _ in texts]

        # 如果禁用重排序，直接使用关键词匹配
        if not enable_rerank:
            logger.info(f"[向量重排序] enable_rerank=False，跳过向量重排序，使用关键词匹配策略，texts数量={len(texts)}")
            return [UnifiedRankingUtils.compute_keyword_match_score(text, query) for text in texts]

        # 使用统一的排序工具接口
        logger.info(f"[向量重排序] enable_rerank=True，使用向量重排序服务，texts数量={len(texts)}，batch_size={batch_size}")
        try:
            scores = await UnifiedRankingUtils._rerank_texts(
                query=query,
                texts=texts,
                batch_size=batch_size
            )
            logger.debug(f"[向量重排序] 向量重排序完成，返回{len(scores)}个分数")
            return scores
        except Exception as e:
            logger.warning(f"[向量重排序] 向量重排序失败，使用关键词匹配降级策略：{e}")
            # 降级策略：使用关键词匹配分数
            return [UnifiedRankingUtils.compute_keyword_match_score(text, query) for text in texts]

            try:
                # rerank 返回格式: [{"relevance_score": 0.985, "index": 1, ...}, ...]
                score_map: Dict[int, float] = {}
                for item in (rerank_scores or []):
                    if not isinstance(item, dict):
                        continue
                    idx = item.get("index")
                    sc = item.get("relevance_score")
                    if isinstance(idx, int) and isinstance(sc, (int, float)):
                        score_map[idx] = float(sc)
                # index 可能从0或1开始，这里按 batch 顺序兜底取 i 或 i+1
                for j in range(len(batch)):
                    if j in score_map:
                        scores.append(score_map[j])
                    elif (j + 1) in score_map:
                        scores.append(score_map[j + 1])
                    else:
                        scores.append(0.0)
            except Exception:
                scores.extend([0.0 for _ in batch])

        # 保证长度一致
        if len(scores) != len(texts):
            if len(scores) > len(texts):
                scores = scores[: len(texts)]
            else:
                scores.extend([0.0 for _ in range(len(texts) - len(scores))])
        return scores

    @classmethod
    async def _select_fields_by_semantic_score(
        cls,
        *,
        query: str,
        object_type: Dict[str, Any],
        searchable_fields: List[Dict[str, Any]],
        semantic_config: Optional[SemanticInstanceRetrievalConfig] = None,
        enable_rerank: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        用重排序模型对属性做语义打分，并按"比例 + 最小/最大"硬截断保留 Top-K 属性。
        """
        if not searchable_fields:
            return []
        if not semantic_config:
            semantic_config = SemanticInstanceRetrievalConfig()

        # ------------------------------------------------------------
        # 快速路径：属性数量较少/预算足够时，属性 rerank 不会改变最终 sub_conditions 集合，
        # 直接跳过 rerank 调用，降低一次外部服务开销。
        #
        # 触发条件（尽量保证"不改变语义行为"）：
        # 1) 预算计算 k == total_fields（不会因为打分而丢属性）
        # 2) max_sub_conditions >= 预计可生成的 sub_conditions 数（属性顺序不会影响最终集合）
        # ------------------------------------------------------------
        total = len(searchable_fields)
        max_sub = int(getattr(semantic_config, "max_semantic_sub_conditions", 10) or 10)
        k = cls._estimate_field_keep_k(total, semantic_config)
        desired = cls._estimate_desired_sub_conditions(searchable_fields)
        if k >= total and desired <= max_sub:
            logger.info(
                f"属性语义打分跳过：total_fields={total}, keep_k={k}, "
                f"desired_sub_conditions={desired} <= max_sub_conditions={max_sub}"
            )
            return searchable_fields

        # 构建属性描述文本并打分（单对象类型版本）
        field_texts = [cls._build_field_rerank_text(object_type, f) for f in searchable_fields]
        logger.info(f"[向量重排序] 属性语义打分：enable_rerank={enable_rerank}，对象类型={object_type_id}，属性数量={len(field_texts)}")
        scores = await cls._rerank_texts(
            query=query,
            texts=field_texts,
            batch_size=int(getattr(semantic_config, "semantic_field_rerank_batch_size", 128) or 128),
            enable_rerank=enable_rerank,
        )

        scored_fields = []
        for idx, f in enumerate(searchable_fields):
            score = float(scores[idx]) if idx < len(scores) else 0.0
            f2 = dict(f)
            f2["semantic_score"] = score
            scored_fields.append(f2)

        return cls._apply_field_budget(scored_fields, semantic_config)

    @classmethod
    def _apply_field_budget(
        cls,
        scored_fields: List[Dict[str, Any]],
        semantic_config: SemanticInstanceRetrievalConfig,
    ) -> List[Dict[str, Any]]:
        """
        对已经带有 semantic_score 的属性列表应用"比例 + 上下限 + 全局预算"的截断策略。
        可被单对象类型/全局多对象类型两种流程复用。
        """
        if not scored_fields:
            return []

        # 按分数降序
        scored_fields = sorted(scored_fields, key=lambda x: float(x.get("semantic_score", 0.0)), reverse=True)

        total = len(scored_fields)
        ratio = float(getattr(semantic_config, "semantic_field_keep_ratio", 0.2) or 0.2)
        keep_min = int(getattr(semantic_config, "semantic_field_keep_min", 5) or 5)
        keep_max = int(getattr(semantic_config, "semantic_field_keep_max", 15) or 15)
        max_sub = int(getattr(semantic_config, "max_semantic_sub_conditions", 10) or 10)

        k = int(math.ceil(total * ratio))
        k = max(k, keep_min)
        k = min(k, keep_max, total)
        k = min(k, max_sub)  # 属性数不应超过总 sub_conditions 预算

        selected = scored_fields[:k] if k > 0 else []
        logger.info(
            f"语义属性筛选：total_fields={total}, keep_ratio={ratio}, keep_min={keep_min}, keep_max={keep_max}, "
            f"max_sub_conditions={max_sub} => selected_fields={len(selected)}"
        )
        return selected

    @classmethod
    async def _select_fields_for_all_object_types(
        cls,
        *,
        query: str,
        object_types: List[Dict[str, Any]],
        semantic_config: Optional[SemanticInstanceRetrievalConfig] = None,
        enable_rerank: bool = True,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        参考"概念召回的对象属性过滤方法"：将所有对象类型的属性集中在一起，统一用 rerank 打分，
        再按对象类型分别应用属性预算策略，得到每个对象类型的 Top-K 语义属性列表。
        """
        if not object_types:
            return {}
        if not semantic_config:
            semantic_config = SemanticInstanceRetrievalConfig()

        # 收集所有对象类型的可检索字段
        field_entries: List[Dict[str, Any]] = []
        # 对于"无需属性打分"的对象类型，直接把属性放入结果（后续仍会应用预算策略）
        preselected_map: Dict[str, List[Dict[str, Any]]] = {}

        max_sub = int(getattr(semantic_config, "max_semantic_sub_conditions", 10) or 10)
        for obj in object_types:
            obj_id = obj.get("concept_id") or obj.get("id")
            if not obj_id:
                continue
            fields = cls._find_semantic_searchable_fields(obj, max_fields=None)
            if not fields:
                continue
            total = len(fields)
            k = cls._estimate_field_keep_k(total, semantic_config)
            desired = cls._estimate_desired_sub_conditions(fields)
            if k >= total and desired <= max_sub:
                # 快速路径：该对象类型属性无需 rerank 打分
                preselected_map[obj_id] = fields
                continue
            for f in fields:
                field_entries.append(
                    {
                        "object_type_id": obj_id,
                        "object_type": obj,
                        "field": f,
                    }
                )

        # 如果所有对象类型都命中快速路径，则直接返回（按预算策略截断）
        if not field_entries and preselected_map:
            logger.info(
                f"全局属性语义打分跳过：object_types={len(preselected_map)}，"
                f"max_sub_conditions={max_sub}"
            )
            selected_map: Dict[str, List[Dict[str, Any]]] = {}
            for obj_id, fields in preselected_map.items():
                # 给一个默认 semantic_score，保证结构一致（可选）
                scored = [dict(f, semantic_score=0.0) for f in (fields or [])]
                selected_map[obj_id] = cls._apply_field_budget(scored, semantic_config)
            return selected_map

        if not field_entries and not preselected_map:
            return {}

        # 全局统一构造属性描述文本并打分（使用统一排序接口）
        # enable_rerank 参数已从函数参数传入，不再从 semantic_config 中读取
        logger.info(f"[向量重排序] 全局属性语义筛选：enable_rerank={enable_rerank}，对象类型数量={len(set(e['object_type_id'] for e in field_entries))}，字段数量={len(field_entries)}")
        
        # 按对象类型分组，使用统一排序接口（确保重要字段默认保留）
        per_type_fields: Dict[str, List[Dict[str, Any]]] = {}
        
        # 先把无需打分的对象类型字段放进去（semantic_score=0）
        for obj_id, fields in preselected_map.items():
            per_type_fields[obj_id] = [dict(f, semantic_score=0.0) for f in (fields or [])]
        
        # 按对象类型分组处理需要打分的字段
        fields_by_obj: Dict[str, List[Dict[str, Any]]] = {}
        for entry in field_entries:
            obj_id = entry["object_type_id"]
            fields_by_obj.setdefault(obj_id, []).append(entry)
        
        # 对每个对象类型使用统一排序接口
        for obj_id, entries in fields_by_obj.items():
            obj_type = entries[0]["object_type"] if entries else {}
            obj_name = obj_type.get("concept_name") or obj_type.get("name") or ""
            primary_keys = obj_type.get("primary_keys", [])
            display_key = obj_type.get("display_key")
            
            # 构建属性列表
            properties = [entry["field"] for entry in entries]
            
            # 使用统一排序接口（确保重要字段默认保留）
            logger.debug(f"[向量重排序] 对象类型属性排序：enable_rerank={enable_rerank}，对象类型={obj_id}，属性数量={len(properties)}")
            ranked_properties = await UnifiedRankingUtils.rank_properties(
                properties=properties,
                object_name=obj_name,
                query=query,
                enable_rerank=enable_rerank,
                strategy=RankingStrategy.RERANK if enable_rerank else RankingStrategy.KEYWORD_MATCH,
                primary_keys=primary_keys,
                display_key=display_key,
                batch_size=int(getattr(semantic_config, "semantic_field_rerank_batch_size", 128) or 128),
            )
            
            # 组装到 per_type_fields
            per_type_fields.setdefault(obj_id, []).extend(ranked_properties)


        # 对每个对象类型分别应用字段预算策略
        selected_map: Dict[str, List[Dict[str, Any]]] = {}
        for obj_id, fields in per_type_fields.items():
            selected_map[obj_id] = cls._apply_field_budget(fields, semantic_config)

        return selected_map
    
    @classmethod
    def _build_semantic_query_conditions(
        cls,
        query: str,
        searchable_fields: List[Dict[str, Any]],
        candidate_limit: int = 50,
        max_sub_conditions: int = 10,
        knn_limit_key: str = "k",
        knn_limit_value: Any = 10,
    ) -> Optional[Dict[str, Any]]:
        """
        构建语义检索查询条件
        
        策略（防止 sub_conditions 爆炸）：
        - 先对属性做语义筛选（由上层完成），这里仅按"预算"分配操作符：
          1) 第一轮：尽量为支持 knn 的属性添加 knn（每属性最多1条）
          2) 第二轮：按属性顺序补充 '=='，再补充 match（每属性最多1条）
          3) 全程保证 sub_conditions 数量不超过 max_sub_conditions
        
        Args:
            query: 查询问题
            searchable_fields: 可搜索属性列表，每个属性包含其支持的操作符信息
            
        Returns:
            API查询条件字典，如果无法构建返回None
        """
        if not searchable_fields:
            return None
        
        sub_conditions = []
        used: Set[Tuple[str, str]] = set()

        def _add_condition(field_name: str, op: str, value: Any, extra: Optional[Dict[str, Any]] = None):
            if len(sub_conditions) >= int(max_sub_conditions):
                return
            key = (field_name, op)
            if key in used:
                return
            cond = {
                "field": field_name,
                "operation": op,
                "value": value,
                "value_from": "const",
            }
            if extra:
                cond.update(extra)
            sub_conditions.append(cond)
            used.add(key)
        
        # 第一轮：优先 knn（仅对支持 knn 的属性）
        # 只对text/string类型的属性添加条件，其他类型（如int）不应该进行条件匹配
        for field_info in searchable_fields:
            if len(sub_conditions) >= int(max_sub_conditions):
                break
            field_name = field_info.get("name")
            supported_ops = field_info.get("condition_operations", []) or []
            if not field_name:
                continue
            # 只对文本类型属性进行条件匹配
            if not cls._is_text_field(field_info):
                continue
            if field_info.get("has_knn") and "knn" in supported_ops:
                _add_condition(
                    field_name=field_name,
                    op="knn",
                    value=query,
                    extra={
                        "limit_key": knn_limit_key,
                        "limit_value": str(knn_limit_value),
                    },
                )

        # 第二轮：补充 ==（更精确）和 match（更召回），直到用满预算
        # 只对text/string类型的属性添加条件，其他类型（如int）不应该进行条件匹配
        for field_info in searchable_fields:
            if len(sub_conditions) >= int(max_sub_conditions):
                break
            field_name = field_info.get("name")
            supported_ops = field_info.get("condition_operations", []) or []
            if not field_name:
                continue
            # 只对文本类型属性进行条件匹配
            if not cls._is_text_field(field_info):
                continue

            # 先补 ==
            if field_info.get("has_exact_match") and "==" in supported_ops:
                _add_condition(field_name=field_name, op="==", value=query)
                if len(sub_conditions) >= int(max_sub_conditions):
                    break

            # 再补 match
            if field_info.get("has_match"):
                preferred_match_op = field_info.get("preferred_match_op")
                if preferred_match_op and preferred_match_op in supported_ops:
                    _add_condition(field_name=field_name, op=preferred_match_op, value=query)
        
        if not sub_conditions:
            return None
        
        # 使用OR逻辑连接所有条件（只要任一属性的任一操作符匹配即可）
        return {
            "condition": {
                "operation": "or",
                "sub_conditions": sub_conditions
            },
            "need_total": True,
            "limit": candidate_limit  # 使用配置的初始召回数量
        }
    
    @classmethod
    async def _call_object_retrieval_api(
        cls,
        kn_id: str,
        object_type_id: str,
        condition: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 5.0
    ) -> Optional[Dict[str, Any]]:
        """兼容接口：委托到 `retrieval/semantic/object_api.py`。"""
        return await call_object_retrieval_api(
            kn_id=kn_id,
            object_type_id=object_type_id,
            condition=condition,
            headers=headers,
            timeout=timeout,
        )
    
    @classmethod
    def _build_instance_description(
        cls,
        instance: Dict[str, Any],
        object_type_id: str,
        schema_info: Dict[str, Any]
    ) -> str:
        """构建实例描述文本，用于向量重排序（使用公共方法）"""
        from ...core.rerank.rerank_utils import build_instance_description
        return build_instance_description(instance, object_type_id, schema_info)
    
    @classmethod
    async def _rerank_instances(
        cls,
        instances: List[Dict[str, Any]],
        query: str,
        object_type_id: str,
        schema_info: Dict[str, Any],
        top_k: int = 10,
        enable_rerank: bool = True
    ) -> List[Dict[str, Any]]:
        """使用向量重排序对实例进行过滤（使用公共方法）"""
        from ...core.rerank.rerank_utils import rerank_instances
        return await rerank_instances(
            instances=instances,
            query=query,
            object_type_id=object_type_id,
            schema_info=schema_info,
            top_k=top_k,
            build_description_func=cls._build_instance_description,
            verbose_logging=False,  # 语义召回使用简单日志
            enable_rerank=enable_rerank
        )
    
    @classmethod
    async def semantic_retrieve_instances(
        cls,
        query: str,
        object_type: Dict[str, Any],
        kn_id: str,
        schema_info: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
        per_type_instance_limit: int = 10,
        candidate_limit: int = 50,
        timeout: float = 5.0,
        semantic_config: Optional[SemanticInstanceRetrievalConfig] = None,
        selected_fields: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        """
        对单个对象类型进行语义实例召回
        
        Args:
            query: 查询问题
            object_type: 对象类型信息（包含properties属性）
            kn_id: 知识网络ID
            schema_info: schema信息
            headers: HTTP请求头
            per_type_instance_limit: 每个对象类型最终返回实例数量上限（重排序后的最终返回数量）
            candidate_limit: 初始召回数量上限（重排序前的候选数量）
            timeout: 请求超时时间（秒）
            
        Returns:
            召回并重排序后的实例列表（最多 per_type_instance_limit 个）
        """
        object_type_id = object_type.get("concept_id") or object_type.get("id")
        if not object_type_id:
            logger.warning(f"对象类型信息中没有找到ID，跳过实例召回")
            return []
        
        # 步骤1: 识别语义检索字段
        searchable_fields = cls._find_semantic_searchable_fields(object_type, max_fields=None)
        
        if not searchable_fields:
            logger.info(f"对象类型 {object_type_id} 没有支持语义检索的属性，跳过实例召回")
            return []
        
        # 统计各类型操作符的数量
        exact_match_count = sum(1 for f in searchable_fields if f.get("has_exact_match"))
        match_count = sum(1 for f in searchable_fields if f.get("has_match"))
        knn_count = sum(1 for f in searchable_fields if f.get("has_knn"))
        
        logger.info(
            f"对象类型 {object_type_id} 语义检索属性："
            f"共 {len(searchable_fields)} 个属性，"
            f"其中支持精确匹配(==)的 {exact_match_count} 个，"
            f"支持全文检索(match)的 {match_count} 个，"
            f"支持向量检索(knn)的 {knn_count} 个"
        )
        
        if not semantic_config:
            semantic_config = SemanticInstanceRetrievalConfig()
        # 步骤2: 属性语义筛选（防止属性过多导致 sub_conditions 爆炸）
        if selected_fields is None:
            enable_rerank = getattr(semantic_config, "enable_rerank", True) if semantic_config else True
            selected_fields = await cls._select_fields_by_semantic_score(
                query=query,
                object_type=object_type,
                searchable_fields=searchable_fields,
                semantic_config=semantic_config,
                enable_rerank=enable_rerank,
            )

        # 步骤3: 构建语义检索查询条件（两轮分配：先 knn，再 ==/match，直到 max_semantic_sub_conditions）
        # knn 的 k 默认用 per_type_instance_limit（与最终每类型保留数一致；且 knn 条件必须带 limit_key/limit_value）
        query_condition = cls._build_semantic_query_conditions(
            query=query,
            searchable_fields=selected_fields,
            candidate_limit=candidate_limit,
            max_sub_conditions=int(getattr(semantic_config, "max_semantic_sub_conditions", 10) or 10),
            knn_limit_key="k",
            knn_limit_value=per_type_instance_limit,
        )
        if not query_condition:
            logger.warning(f"无法为对象类型 {object_type_id} 构建查询条件")
            return []
        
        # NOTE: 不在正常流程中打印构建的查询条件，避免日志过多；
        # 仅在查询失败时（见 _call_object_retrieval_api 的异常处理）打印请求Body用于排错。
        
        # 步骤3: 调用对象检索接口
        logger.info(f"开始对对象类型 {object_type_id} 进行语义实例召回，初始召回数量: {candidate_limit}")
        api_result = await cls._call_object_retrieval_api(
            kn_id=kn_id,
            object_type_id=object_type_id,
            condition=query_condition,
            headers=headers,
            timeout=timeout
        )
        
        if not api_result:
            logger.warning(f"对象类型 {object_type_id} 的实例召回失败")
            return []
        
        # 提取实例数据
        instances = api_result.get("datas", [])
        if not instances:
            logger.info(f"对象类型 {object_type_id} 没有召回任何实例")
            return []
        
        logger.info(f"对象类型 {object_type_id} 召回 {len(instances)} 个实例")
        
        # 步骤4: 向量重排序
        enable_rerank = getattr(semantic_config, "enable_rerank", True) if semantic_config else True
        reranked_instances = await cls._rerank_instances(
            instances=instances,
            query=query,
            object_type_id=object_type_id,
            schema_info=schema_info,
            top_k=per_type_instance_limit,
            enable_rerank=enable_rerank
        )
        
        logger.info(f"对象类型 {object_type_id} 语义实例召回完成，最终返回 {len(reranked_instances)} 个实例")
        
        return reranked_instances

    @classmethod
    async def semantic_retrieve_candidate_instances(
        cls,
        query: str,
        object_type: Dict[str, Any],
        kn_id: str,
        schema_info: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
        candidate_limit: int = 50,
        timeout: float = 5.0,
        semantic_config: Optional[SemanticInstanceRetrievalConfig] = None,
        selected_fields: Optional[List[Dict[str, Any]]] = None,
        knn_limit_value: Any = 10,
    ) -> List[Dict[str, Any]]:
        """
        对单个对象类型进行“候选实例召回”（不做rerank、不做过滤）。
        
        用于多关键词综合检索：先扩展候选池（按关键词并集），再用完整query做统一过滤/重排。
        """
        object_type_id = object_type.get("concept_id") or object_type.get("id")
        if not object_type_id:
            logger.warning("对象类型信息中没有找到ID，跳过候选实例召回")
            return []
        
        # 识别语义检索属性并构建查询条件
        searchable_fields = cls._find_semantic_searchable_fields(object_type, max_fields=None)
        if not searchable_fields:
            logger.info(f"对象类型 {object_type_id} 没有支持语义检索的属性，跳过候选实例召回")
            return []

        if not semantic_config:
            semantic_config = SemanticInstanceRetrievalConfig()

        if selected_fields is None:
            enable_rerank = getattr(semantic_config, "enable_rerank", True) if semantic_config else True
            selected_fields = await cls._select_fields_by_semantic_score(
                query=query,
                object_type=object_type,
                searchable_fields=searchable_fields,
                semantic_config=semantic_config,
                enable_rerank=enable_rerank,
            )
        
        # 候选召回不做 rerank/截断，但 knn 仍需带 limit_key/limit_value；默认使用 k=10（可由调用方覆盖）
        query_condition = cls._build_semantic_query_conditions(
            query=query,
            searchable_fields=selected_fields,
            candidate_limit=candidate_limit,
            max_sub_conditions=int(getattr(semantic_config, "max_semantic_sub_conditions", 10) or 10),
            knn_limit_key="k",
            knn_limit_value=knn_limit_value,
        )
        if not query_condition:
            logger.warning(f"无法为对象类型 {object_type_id} 构建候选召回查询条件")
            return []
        
        # 调用对象检索接口，直接返回候选 datas
        api_result = await cls._call_object_retrieval_api(
            kn_id=kn_id,
            object_type_id=object_type_id,
            condition=query_condition,
            headers=headers,
            timeout=timeout
        )
        if not api_result:
            return []
        
        instances = api_result.get("datas", [])
        if not instances:
            return []
        
        if not isinstance(instances, list):
            logger.warning(f"对象类型 {object_type_id} 候选实例召回返回datas非list，忽略")
            return []
        
        return instances

    @classmethod
    async def semantic_retrieve_candidates_for_all(
        cls,
        query: str,
        object_types: List[Dict[str, Any]],
        kn_id: str,
        schema_info: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
        candidate_limit: int = 50,
        max_concurrent: int = 5,
        timeout: float = 5.0,
        semantic_config: Optional[SemanticInstanceRetrievalConfig] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        对所有对象类型进行“候选实例召回”（并发执行，不做rerank、不做过滤）。
        
        Returns:
            {object_type_id: [raw_instances]}
        """
        if not object_types:
            return {}

        # 全局统一属性语义打分，再按对象类型分配 Top-K 属性，减少重复打分
        selected_fields_map: Dict[str, List[Dict[str, Any]]] = await cls._select_fields_for_all_object_types(
            query=query, object_types=object_types, semantic_config=semantic_config, enable_rerank=enable_rerank
        )
        
        async def _retrieve_one(obj_type: Dict[str, Any]) -> List[Dict[str, Any]]:
            obj_id = obj_type.get("concept_id") or obj_type.get("id")
            selected_fields = selected_fields_map.get(obj_id, [])
            return await cls.semantic_retrieve_candidate_instances(
                query=query,
                object_type=obj_type,
                kn_id=kn_id,
                schema_info=schema_info,
                headers=headers,
                candidate_limit=candidate_limit,
                timeout=timeout,
                semantic_config=semantic_config,
                selected_fields=selected_fields,
            )

        # 与旧逻辑一致：不吞异常，任一失败直接抛
        return await retrieve_map_for_all_object_types(
            object_types=object_types,
            retrieve_one=_retrieve_one,
            max_concurrent=max_concurrent,
            log_prefix="候选实例召回",
            swallow_exceptions=False,
        )

    @classmethod
    async def rerank_instance_map(
        cls,
        instance_map: Dict[str, List[Dict[str, Any]]],
        query: str,
        schema_info: Dict[str, Any],
        per_type_top_k: Optional[int] = None,
        top_k: Optional[int] = None,
        enable_rerank: bool = True,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        对候选实例 map 做统一 rerank（全局一次 rerank + 每对象类型截断），
        用于综合关键词场景的最终排序/预筛。
        """
        if per_type_top_k is None:
            per_type_top_k = top_k if top_k is not None else 10
        try:
            per_type_top_k = int(per_type_top_k)
        except Exception:
            per_type_top_k = 10
        if per_type_top_k <= 0:
            per_type_top_k = 1
        # 如果没有提供 semantic_config，使用默认的 enable_rerank
        if enable_rerank is None:
            enable_rerank = True
        return await cls._global_rerank_and_trim_instance_map(
            instance_map=instance_map,
            query=query,
            schema_info=schema_info,
            per_type_top_k=per_type_top_k,
            semantic_config=None,
            enable_rerank=enable_rerank,
        )
    
    @classmethod
    async def semantic_retrieve_instances_for_all(
        cls,
        query: str,
        object_types: List[Dict[str, Any]],
        kn_id: str,
        schema_info: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
        per_type_instance_limit: Optional[int] = None,
        top_k: Optional[int] = None,
        candidate_limit: int = 50,
        max_concurrent: int = 5,
        timeout: float = 5.0,
        semantic_config: Optional[SemanticInstanceRetrievalConfig] = None,
        enable_rerank: bool = True,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        对所有对象类型进行语义实例召回（并发执行）
        支持评分、过滤和关联判定功能
        
        Args:
            query: 查询问题
            object_types: 对象类型列表
            kn_id: 知识网络ID
            schema_info: schema信息
            headers: HTTP请求头
            per_type_instance_limit: 每个对象类型最终返回实例数量上限（优先使用该参数）
            top_k: 兼容历史入参（等价于 per_type_instance_limit，后续将移除）
            candidate_limit: 每个对象类型的初始召回数量上限（重排序前的候选数量）
            max_concurrent: 最大并发数
            timeout: 每个请求的超时时间（秒）
            semantic_config: 语义实例召回配置
            
        Returns:
            字典，格式为 {object_type_id: [instances]}
        """
        if not object_types:
            return {}

        # 兼容：历史上使用 top_k 表示每类型实例上限
        if per_type_instance_limit is None:
            per_type_instance_limit = top_k if top_k is not None else 10
        try:
            per_type_instance_limit = int(per_type_instance_limit)
        except Exception:
            per_type_instance_limit = 10
        if per_type_instance_limit <= 0:
            per_type_instance_limit = 1

        # 若调用方未提供配置，使用默认配置
        if not semantic_config:
            semantic_config = SemanticInstanceRetrievalConfig()
        
        return await cls._semantic_retrieve_with_filtering(
            query=query,
            object_types=object_types,
            kn_id=kn_id,
            schema_info=schema_info,
            headers=headers,
            per_type_instance_limit=per_type_instance_limit,
            candidate_limit=candidate_limit,
            max_concurrent=max_concurrent,
            timeout=timeout,
            semantic_config=semantic_config,
            enable_rerank=enable_rerank,
        )

    @classmethod
    async def _basic_retrieve_instances_for_all(
        cls,
        *,
        query: str,
        object_types: List[Dict[str, Any]],
        kn_id: str,
        schema_info: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
        per_type_instance_limit: int = 10,
        candidate_limit: int = 50,
        max_concurrent: int = 5,
        timeout: float = 5.0,
        semantic_config: Optional[SemanticInstanceRetrievalConfig] = None,
        enable_rerank: bool = True,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        基础语义实例召回（并发执行）：对每个对象类型做语义检索（不做实例rerank），
        然后全局一次实例rerank并按 per_type_instance_limit 截断。

        注意：该方法仅用于“增强过滤”内部生成候选池，避免与外部总入口互相递归。
        """
        if not object_types:
            return {}

        # 全局统一属性语义打分，再按对象类型分配 Top-K 属性，减少重复打分
        selected_fields_map: Dict[str, List[Dict[str, Any]]] = await cls._select_fields_for_all_object_types(
            query=query, object_types=object_types, semantic_config=semantic_config, enable_rerank=enable_rerank
        )

        async def _retrieve_one(obj_type: Dict[str, Any]) -> List[Dict[str, Any]]:
            # 与旧逻辑一致：单个对象类型失败时返回空列表，不影响整体
            try:
                obj_id = obj_type.get("concept_id") or obj_type.get("id")
                selected_fields = selected_fields_map.get(obj_id, [])
                # 这里先只做候选召回，不做 per-type 实例 rerank，后续会全局一次 rerank
                return await cls.semantic_retrieve_candidate_instances(
                    query=query,
                    object_type=obj_type,
                    kn_id=kn_id,
                    schema_info=schema_info,
                    headers=headers,
                    candidate_limit=candidate_limit,
                    timeout=timeout,
                    semantic_config=semantic_config,
                    selected_fields=selected_fields,
                    knn_limit_value=per_type_instance_limit,
                )
            except Exception as e:
                logger.warning(
                    f"对象类型 {obj_type.get('concept_id') or obj_type.get('id')} 的实例召回失败: {str(e)}",
                    exc_info=True,
                )
                return []

        candidate_map = await retrieve_map_for_all_object_types(
            object_types=object_types,
            retrieve_one=_retrieve_one,
            max_concurrent=max_concurrent,
            log_prefix="语义实例召回",
            swallow_exceptions=True,
        )
        # 全局一次实例 rerank，并按每类型 per_type_instance_limit 截断
        # enable_rerank 参数已从函数参数传入，不再从 semantic_config 中读取
        return await cls._global_rerank_and_trim_instance_map(
            instance_map=candidate_map,
            query=query,
            schema_info=schema_info,
            per_type_top_k=per_type_instance_limit,
            semantic_config=semantic_config,
            enable_rerank=enable_rerank,
        )
    
    @classmethod
    async def _semantic_retrieve_with_filtering(
        cls,
        query: str,
        object_types: List[Dict[str, Any]],
        kn_id: str,
        schema_info: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
        per_type_instance_limit: int = 10,
        candidate_limit: int = 50,
        max_concurrent: int = 5,
        timeout: float = 5.0,
        semantic_config: Optional[SemanticInstanceRetrievalConfig] = None,
        enable_rerank: bool = True,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        使用增强版逻辑进行语义实例召回，包括评分、过滤和关联判定
        
        Args:
            query: 用户查询
            object_types: 对象类型列表
            kn_id: 知识网络ID
            schema_info: Schema信息
            headers: HTTP请求头
            per_type_instance_limit: 每个对象类型最终返回实例数量上限
            candidate_limit: 每个对象类型的初始召回数量上限
            max_concurrent: 最大并发数
            timeout: 请求超时时间（秒）
            semantic_config: 语义实例召回配置
            
        Returns:
            字典，格式为 {object_type_id: [instances]}，只包含核心实例和上下文实例
        """
        if not semantic_config:
            semantic_config = SemanticInstanceRetrievalConfig()
        
        logger.info(f"开始语义实例召回，查询: {query}")
        
        # 执行基础语义实例召回
        logger.info("执行基础语义实例召回")
        instance_map = await cls._basic_retrieve_instances_for_all(
            query=query,
            object_types=object_types,
            kn_id=kn_id,
            schema_info=schema_info,
            headers=headers,
            per_type_instance_limit=per_type_instance_limit,
            candidate_limit=candidate_limit,
            max_concurrent=max_concurrent,
            timeout=timeout,
            semantic_config=semantic_config,
            enable_rerank=enable_rerank,
        )
        
        # 直接按 per_type_instance_limit 截断返回
        trimmed_map: Dict[str, List[Dict[str, Any]]] = {}
        for obj_id, insts in (instance_map or {}).items():
            if not isinstance(insts, list):
                continue
            trimmed_map[obj_id] = insts[:per_type_instance_limit]
        return trimmed_map

    @classmethod
    async def filter_instance_map_with_filtering(
        cls,
        instance_map: Dict[str, List[Dict[str, Any]]],
        query: str,
        object_types: List[Dict[str, Any]],
        kn_id: str,
        schema_info: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
        semantic_config: Optional[SemanticInstanceRetrievalConfig] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        对"外部提供的候选实例池"执行过滤（基于直接相关性评分）。
        
        典型用途：多关键词综合检索（先按关键词并集扩展候选，再用完整query统一过滤）。
        """
        return await cls._filter_instance_map_with_filtering(
            instance_map=instance_map,
            query=query,
            object_types=object_types,
            kn_id=kn_id,
            schema_info=schema_info,
            headers=headers,
            semantic_config=semantic_config
        )

    @classmethod
    async def _filter_instance_map_with_filtering(
        cls,
        instance_map: Dict[str, List[Dict[str, Any]]],
        query: str,
        object_types: List[Dict[str, Any]],
        kn_id: str,
        schema_info: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
        semantic_config: Optional[SemanticInstanceRetrievalConfig] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        if not semantic_config:
            semantic_config = SemanticInstanceRetrievalConfig()
        
        # 初始化评分器（只使用直接相关性）
        scorer = InstanceScorer(
            direct_relevance_weight=1.0,
            path_importance_weight=0.0,
            min_direct_relevance=semantic_config.min_direct_relevance,
            min_final_score=0.0,
            keep_direct_matches=False,
        )
        
        # 构建对象类型schema映射（包含primary_keys和display_key）
        object_type_schema_map: Dict[str, Dict[str, Any]] = {}
        for obj_type in (schema_info or {}).get("object_types", []):
            obj_type_id = obj_type.get("concept_id") or obj_type.get("id")
            if obj_type_id:
                object_type_schema_map[obj_type_id] = {
                    "primary_keys": obj_type.get("primary_keys", []) or [],
                    "display_key": obj_type.get("display_key")
                }
        
        # 收集候选实例并丰富instance_id/instance_name
        all_candidate_instances: List[Dict[str, Any]] = []
        object_type_map: Dict[str, str] = {}
        skipped_object_types_no_schema = 0
        skipped_instances_enrich_failed = 0
        skipped_instances_missing_obj_type = 0
        
        for obj_type in object_types or []:
            obj_id = obj_type.get("concept_id") or obj_type.get("id")
            obj_name = obj_type.get("concept_name") or obj_type.get("name", "")
            if not obj_id:
                skipped_instances_missing_obj_type += 1
                continue
            object_type_map[obj_id] = obj_name
            
            obj_schema = object_type_schema_map.get(obj_id, {})
            primary_keys = obj_schema.get("primary_keys", []) or []
            display_key = obj_schema.get("display_key")
            if not obj_schema:
                skipped_object_types_no_schema += 1
            
            instances = (instance_map or {}).get(obj_id, []) or []
            for inst in instances:
                if not isinstance(inst, dict):
                    continue
                inst["object_type_id"] = obj_id
                inst["object_type_name"] = obj_name
                
                enriched_inst = InstanceUtils.enrich_instance_data(
                    inst, obj_id, primary_keys, display_key, raise_on_error=False
                )
                if not enriched_inst:
                    skipped_instances_enrich_failed += 1
                    continue
                all_candidate_instances.append(enriched_inst)
        
        if not all_candidate_instances:
            logger.warning("没有候选实例可用于过滤")
            return {}
        
        logger.info(f"候选池准备完成，共 {len(all_candidate_instances)} 个候选实例，将使用完整query进行过滤")
        if skipped_object_types_no_schema or skipped_instances_enrich_failed or skipped_instances_missing_obj_type:
            logger.warning(
                "候选实例整理过程中有数据被跳过："
                f"缺少schema的对象类型数={skipped_object_types_no_schema}, "
                f"enrich失败的实例数={skipped_instances_enrich_failed}, "
                f"缺少对象类型ID的输入对象类型数={skipped_instances_missing_obj_type}"
            )

        # 1) 计算完整 query 的直接相关性分数（主信号）
        direct_relevance_scores = await scorer.compute_direct_relevance_scores(
            instances=all_candidate_instances,
            query=query,
            object_type_map=object_type_map
        )

        # 2) 多关键词覆盖度信号：对每个关键词分别计算语义分，统计命中次数与累积分数
        keywords: List[str] = cls._split_query_terms(query)

        # 仅当存在多个关键词时才计算覆盖度；单关键词退化为纯 direct_relevance 排序
        keyword_score_maps: List[Dict[str, float]] = []
        if len(keywords) > 1:
            logger.info(f"多关键词语义合并：query 被拆分为 {len(keywords)} 个关键词={keywords}")
            for kw in keywords:
                try:
                    kw_scores = await scorer.compute_direct_relevance_scores(
                        instances=all_candidate_instances,
                        query=kw,
                        object_type_map=object_type_map
                    )
                    keyword_score_maps.append(kw_scores or {})
                except Exception as e:
                    logger.warning(
                        f"计算关键词 '{kw}' 语义分数时出错，将跳过该关键词参与覆盖度统计: {e}"
                    )

        # 3) 组合打分：Full query 语义分 + 关键词覆盖度 + 命中次数
        alpha = 0.7  # 完整 query 语义分权重
        beta = 0.3   # 关键词覆盖度分权重
        gamma = 0.05 # 关键词命中次数奖励权重
        coverage_threshold = semantic_config.min_direct_relevance
        exact_name_match_score = float(getattr(semantic_config, "exact_name_match_score", 0.85) or 0.85)

        final_scores_simple: Dict[str, float] = {}
        per_type_buckets: Dict[str, List[Dict[str, Any]]] = {}

        for inst in all_candidate_instances:
            obj_id = inst.get("object_type_id")
            inst_id = inst.get("instance_id") or inst.get("id")
            if not obj_id or not inst_id:
                continue

            base_score = float(direct_relevance_scores.get(inst_id, 0.0) or 0.0)
            # 直接命中（多关键词场景的"保底"）：任一关键词与实例名完全相等时，提升基础分
            # 说明：仅做"完全相等"而非包含判断，避免如关键词"咳嗽"误命中"止咳片"等。
            inst_name_raw = inst.get("instance_name") or inst.get("name") or ""
            inst_name = str(inst_name_raw).strip().lower() if inst_name_raw else ""
            if inst_name and keywords and any(inst_name == kw for kw in keywords):
                if base_score < exact_name_match_score:
                    base_score = exact_name_match_score

            # 关键词覆盖度与命中次数
            coverage_score = 0.0
            hit_count = 0
            if keyword_score_maps:
                for kw_scores in keyword_score_maps:
                    s_kw = float(kw_scores.get(inst_id, 0.0) or 0.0)
                    if s_kw >= coverage_threshold:
                        hit_count += 1
                        coverage_score += s_kw

            if hit_count > 0:
                coverage_score = coverage_score / hit_count

            final_score = alpha * base_score + beta * coverage_score + gamma * float(hit_count)
            final_scores_simple[inst_id] = final_score
            # 将最终分数挂到实例上，供后续全局排序使用
            inst["final_score"] = final_score

            # 收集到按对象类型分桶的结构中，稍后做 per_type 截断
            per_type_buckets.setdefault(obj_id, []).append(inst)

        per_type_limit = semantic_config.per_type_instance_limit
        trimmed_result: Dict[str, List[Dict[str, Any]]] = {}
        for obj_id, insts in per_type_buckets.items():
            # 按 final_score 排序
            sorted_insts = sorted(
                insts,
                key=lambda x: final_scores_simple.get(
                    x.get("instance_id") or x.get("id"), 0.0
                ),
                reverse=True,
            )
            trimmed_result[obj_id] = sorted_insts[:per_type_limit]

        logger.info(
            f"过滤完成：对象类型数={len(trimmed_result)}，每类型上限={per_type_limit}"
        )
        return trimmed_result

