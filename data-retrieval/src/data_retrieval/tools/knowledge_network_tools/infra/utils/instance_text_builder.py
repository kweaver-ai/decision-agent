# -*- coding: utf-8 -*-
"""
实例文本构建器

背景：
- 语义实例召回/条件召回在 rerank 阶段使用 `rerank_utils.build_instance_description`
- direct_relevance 打分在 `InstanceScorer` 内部又实现了一套 `_build_instance_description`

这两套逻辑在字段选择、排序稳定性、长度控制上存在不一致，容易导致：
- 分数波动（同一实例在不同阶段文本不同）
- 文本过长（全量拼接所有字符串字段）
- 字段顺序不稳定（依赖 dict 遍历顺序/数据源差异）

本模块提供一个统一的 builder，供多个阶段复用，并提供可控的配置项。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


@dataclass(frozen=True)
class InstanceTextBuildOptions:
    """
    实例文本构建选项

    注意：默认值偏“保守兼容”，避免一次性改变线上行为过大。
    """

    # 是否在文本里包含对象类型名（对“公司/人员/产品”等类型区分有帮助）
    include_object_type_name: bool = False

    # 是否在文本里包含 instance_id（通常噪声较大，默认不展示）
    include_instance_id: bool = False

    # 是否拼接数值类型属性（金额/数量/年份类查询非常依赖数值；rerank 阶段默认仍关闭以兼容）
    include_numeric_properties: bool = False

    # 最多拼接的属性数量；None 表示不限制（会受 max_total_chars 约束）
    max_properties: Optional[int] = None

    # 单个字段值最大长度（字符），超出截断
    max_value_chars: int = 200

    # 最终整段文本最大长度（字符），超出截断
    max_total_chars: int = 2000

    # 输出格式：inline（逗号拼接）/ structured（多行标签）
    format: str = "inline"

    # 属性分隔符（inline 模式使用）
    inline_sep: str = "，"

    # 需要排除的字段名黑名单（在属性拼接阶段生效）
    excluded_keys: Tuple[str, ...] = (
        "mapped_field",
        "unique_identities",
        "object_type_id",
        "object_type_name",
        "properties",
        "instance_id",
        "id",
        "instance_name",
        "name",
        "scores",
        "source_info",
        "keyword_sources",
        "final_score",
        "relevance_score",
        "direct_score",
        "rerank_score",
        "score",
    )


# ==============================
# 统一策略（激进版）
# ==============================
# direct_relevance 与 rerank 阶段共用同一份实例文本策略：
# - structured 多行标签，便于 cross-encoder/rerank 识别字段边界
# - 包含类型名 + 数值属性，提升“金额/数量/年份”等问法的召回与评分稳定性
# - max_properties/max_total_chars 控制噪声与成本，避免字段爆炸
UNIFIED_INSTANCE_TEXT_OPTIONS = InstanceTextBuildOptions(
    include_object_type_name=True,
    include_instance_id=False,
    include_numeric_properties=True,
    max_properties=10,
    max_value_chars=200,
    max_total_chars=1800,
    format="structured",
    inline_sep="，",
)


def _safe_str(v: Any) -> str:
    try:
        s = str(v)
    except Exception:
        return ""
    return s.strip()


def _truncate(s: str, max_chars: int) -> str:
    if max_chars is None or max_chars <= 0:
        return ""
    if len(s) <= max_chars:
        return s
    return s[: max_chars - 1] + "…"


def _get_object_type_meta(schema_info: Optional[Dict[str, Any]], object_type_id: Optional[str]) -> Tuple[Optional[str], List[str]]:
    """
    从 schema_info 中提取 object_type_name / primary_keys
    """
    if not schema_info or not object_type_id:
        return None, []

    for obj in schema_info.get("object_types", []) or []:
        if (obj.get("concept_id") or obj.get("id")) == object_type_id:
            name = obj.get("concept_name") or obj.get("name")
            pks = obj.get("primary_keys") or []
            return (name if isinstance(name, str) else None), (pks if isinstance(pks, list) else [])
    return None, []


def _get_display_key(schema_info: Optional[Dict[str, Any]], object_type_id: Optional[str]) -> Optional[str]:
    if not schema_info or not object_type_id:
        return None
    for obj in schema_info.get("object_types", []) or []:
        if (obj.get("concept_id") or obj.get("id")) == object_type_id:
            dk = obj.get("display_key")
            return dk if isinstance(dk, str) and dk.strip() else None
    return None


def _normalize_properties(instance: Dict[str, Any]) -> Dict[str, Any]:
    """
    兼容两种格式：
    - instance['properties'] 是 dict
    - instance 顶层就是 properties（或 properties 不是 dict）
    """
    props = instance.get("properties", None)
    if isinstance(props, dict):
        return props

    # 回退：从顶层提取（尽量去掉结构字段）
    filtered: Dict[str, Any] = {}
    for k, v in (instance or {}).items():
        if k in ("properties",):
            continue
        filtered[k] = v
    return filtered


def _pick_instance_name(
    instance: Dict[str, Any],
    properties: Dict[str, Any],
    *,
    object_type_id: Optional[str],
    schema_info: Optional[Dict[str, Any]],
    object_type_name_hint: Optional[str],
) -> str:
    """
    尽量稳定地挑选一个“展示名”
    """
    instance_id = _safe_str(instance.get("instance_id") or instance.get("id") or "")
    instance_name = _safe_str(instance.get("instance_name") or instance.get("name") or "")
    if instance_name and instance_name != instance_id:
        return instance_name

    display_key = _get_display_key(schema_info, object_type_id)
    if display_key and display_key in properties:
        v = _safe_str(properties.get(display_key))
        if v and v != instance_id:
            return v

    # 主键兜底：只取第一个有值的主键字段
    _, primary_keys = _get_object_type_meta(schema_info, object_type_id)
    for pk in primary_keys or []:
        if pk in properties:
            v = _safe_str(properties.get(pk))
            if v:
                return v

    # 最后：类型名 + instance_id
    ot_name = _safe_str(object_type_name_hint or "") or _safe_str(_get_object_type_meta(schema_info, object_type_id)[0] or "")
    if ot_name and instance_id:
        return f"{ot_name}实例 {instance_id}"
    if ot_name:
        return f"{ot_name}实例"
    if instance_id:
        return f"实例 {instance_id}"
    return "未知实例"


def _iter_property_kv(
    properties: Dict[str, Any],
    *,
    include_numeric: bool,
    excluded: Sequence[str],
    display_key: Optional[str],
) -> List[Tuple[str, str]]:
    kvs: List[Tuple[str, str]] = []
    for k, v in (properties or {}).items():
        if not isinstance(k, str) or not k:
            continue
        if k in excluded:
            continue
        if display_key and k == display_key:
            # display_key 通常已用于 name，不再重复拼接
            continue

        if isinstance(v, str):
            s = v.strip()
            if not s:
                continue
            kvs.append((k, s))
            continue

        if include_numeric and isinstance(v, (int, float)):
            kvs.append((k, _safe_str(v)))
            continue

        # 其他类型默认不拼接（避免列表/对象展开造成噪声与膨胀）
    return kvs


def _stable_sort_kvs(kvs: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    """
    稳定排序：优先一些“常见语义字段”，其余按 key 字典序。
    """
    priority = (
        "desc",
        "description",
        "简介",
        "摘要",
        "summary",
        "备注",
        "comment",
        "行业",
        "领域",
        "标签",
        "国家",
        "地区",
        "城市",
        "省份",
        "时间",
        "日期",
        "年份",
    )
    pri_map = {k: i for i, k in enumerate(priority)}

    def _rank(item: Tuple[str, str]) -> Tuple[int, str]:
        key = item[0]
        return (pri_map.get(key, 10_000), key)

    return sorted(kvs, key=_rank)


def build_instance_text(
    instance: Dict[str, Any],
    *,
    object_type_id: Optional[str] = None,
    schema_info: Optional[Dict[str, Any]] = None,
    object_type_name: Optional[str] = None,
    options: Optional[InstanceTextBuildOptions] = None,
) -> str:
    """
    构建实例文本（统一入口）
    """
    if not isinstance(instance, dict):
        return ""

    opts = options or InstanceTextBuildOptions()
    props = _normalize_properties(instance)
    display_key = _get_display_key(schema_info, object_type_id)

    name = _pick_instance_name(
        instance,
        props,
        object_type_id=object_type_id,
        schema_info=schema_info,
        object_type_name_hint=object_type_name,
    )

    ot_name = _safe_str(object_type_name or "") or _safe_str(_get_object_type_meta(schema_info, object_type_id)[0] or "")
    inst_id = _safe_str(instance.get("instance_id") or instance.get("id") or "")

    kvs = _iter_property_kv(
        props,
        include_numeric=opts.include_numeric_properties,
        excluded=opts.excluded_keys,
        display_key=display_key,
    )
    kvs = _stable_sort_kvs(kvs)

    # 截断：属性数量
    if opts.max_properties is not None and opts.max_properties >= 0:
        kvs = kvs[: opts.max_properties]

    # 截断：单值
    kvs = [(k, _truncate(v, opts.max_value_chars)) for k, v in kvs]

    if opts.format == "structured":
        lines: List[str] = [f"名称: {name}"]
        if opts.include_object_type_name and ot_name:
            lines.append(f"类型: {ot_name}")
        if opts.include_instance_id and inst_id:
            lines.append(f"主键: {inst_id}")
        if kvs:
            lines.append("属性:")
            for k, v in kvs:
                lines.append(f"- {k}: {v}")
        text = "\n".join(lines)
        return _truncate(text, opts.max_total_chars)

    # inline
    parts: List[str] = [name] if name else []
    if opts.include_object_type_name and ot_name:
        parts.append(ot_name)
    if opts.include_instance_id and inst_id:
        parts.append(f"实例ID：{inst_id}")
    if kvs:
        props_text = opts.inline_sep.join([f"{k}：{v}" for k, v in kvs])
        parts.append(f"属性：{props_text}")
    text = opts.inline_sep.join([p for p in parts if p])
    return _truncate(text, opts.max_total_chars)


