import contextvars
from dataclasses import dataclass
import time
from typing import Dict, List, Optional

# 使用 contextvar 存储当前请求的计时累加器
_api_cost_ctx: contextvars.ContextVar[Dict[str, float]] = contextvars.ContextVar("_api_cost_ctx", default=None)
_req_start_ctx: contextvars.ContextVar[float] = contextvars.ContextVar("_req_start_ctx", default=None)


@dataclass(frozen=True)
class ApiSpan:
    """
    单次API调用的时间片段（用于定位最慢接口、并发去重统计等）。

    注意：start/end 为 time.monotonic() 的秒级时间戳。
    """

    bucket: str
    label: str
    start: float
    end: float
    elapsed_ms: float


# 记录每个API调用的时间段（带元信息），用于：
# - 计算并发去重后的 union 耗时（墙钟口径）
# - 输出 Top-N 最慢请求（定位瓶颈接口）
_api_spans_ctx: contextvars.ContextVar[List[ApiSpan]] = contextvars.ContextVar("_api_spans_ctx", default=None)


def set_timing_ctx(api_cost: Dict[str, float], start_ts: float) -> None:
    _api_cost_ctx.set(api_cost)
    _req_start_ctx.set(start_ts)
    _api_spans_ctx.set([])


def clear_timing_ctx() -> None:
    _api_cost_ctx.set(None)
    _req_start_ctx.set(None)
    _api_spans_ctx.set(None)


def record_span(bucket: str, start: float, end: float, label: Optional[str] = None) -> None:
    """
    记录一次API调用时间段，并累加到对应 bucket。
    """
    if start is None or end is None:
        return
    if end < start:
        # 极端情况下避免负值；不记录
        return
    elapsed_ms = (end - start) * 1000.0

    ctx = _api_cost_ctx.get()
    if ctx is not None:
        ctx[bucket] = ctx.get(bucket, 0.0) + float(elapsed_ms)

    spans = _api_spans_ctx.get()
    if spans is not None:
        spans.append(
            ApiSpan(
                bucket=bucket,
                label=label or bucket,
                start=float(start),
                end=float(end),
                elapsed_ms=float(elapsed_ms),
            )
        )


def add_cost(bucket: str, elapsed_ms: float) -> None:
    if elapsed_ms is None:
        return
    ctx = _api_cost_ctx.get()
    if ctx is None:
        return
    ctx[bucket] = ctx.get(bucket, 0.0) + float(elapsed_ms)
    # 同时记录时间区间（用于 union 及最慢请求定位）。
    spans = _api_spans_ctx.get()
    if spans is not None:
        now = time.monotonic()
        spans.append(
            ApiSpan(
                bucket=bucket,
                label=bucket,
                start=now - float(elapsed_ms) / 1000.0,
                end=now,
                elapsed_ms=float(elapsed_ms),
            )
        )


def compute_api_union_ms(bucket: Optional[str] = None) -> float:
    """
    计算API调用的并集耗时（去重并发区间）
    """
    spans = _api_spans_ctx.get()
    if not spans:
        return 0.0
    intervals = [(s.start, s.end) for s in spans if (bucket is None or s.bucket == bucket)]
    if not intervals:
        return 0.0
    # 按开始时间排序并合并
    sorted_intervals = sorted(intervals, key=lambda x: x[0])
    merged = []
    for s, e in sorted_intervals:
        if not merged or s > merged[-1][1]:
            merged.append([s, e])
        else:
            merged[-1][1] = max(merged[-1][1], e)
    union_seconds = sum(e - s for s, e in merged)
    return union_seconds * 1000.0


def get_top_slowest_api_spans(n: int = 5, bucket: Optional[str] = None) -> List[ApiSpan]:
    """
    返回最慢的 Top-N API 调用（按单次 elapsed_ms 降序）。
    """
    spans = _api_spans_ctx.get() or []
    filtered = [s for s in spans if bucket is None or s.bucket == bucket]
    filtered.sort(key=lambda x: x.elapsed_ms, reverse=True)
    return filtered[: max(int(n), 0)]


class api_timer:
    """轻量计时上下文，用于包裹单次API调用。"""

    def __init__(self, bucket: str, label: Optional[str] = None):
        self.bucket = bucket
        self.label = label
        self.start = None

    def __enter__(self):
        self.start = time.monotonic()
        return self

    def __exit__(self, exc_type, exc, tb):
        if self.start is not None:
            end = time.monotonic()
            record_span(self.bucket, self.start, end, label=self.label)
        # 不拦截异常
        return False

