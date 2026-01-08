# -*- coding: utf-8 -*-
"""
语义实例 nodes 的多轮存储与并集/增量计算

背景：
- 概念流程下会执行语义实例召回，最终输出为扁平 nodes（对齐条件召回 nodes 风格）
- 多轮对话需要支持：
  - return_union=True：返回所有轮次 nodes 并集
  - return_union=False：返回当前轮次相对历史并集的增量 nodes
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Set, Tuple

from data_retrieval.logs.logger import logger

from ._base import _SessionBase


class _SemanticNodesMixin(_SessionBase):
    @staticmethod
    def _node_dedup_key(node: Any) -> str:
        """
        为 nodes 生成稳定去重键（跨轮并集/增量需要）：
        - 优先：object_type_id + unique_identities（最稳定）
        - 其次：instance_id（若存在）
        - 最后：稳定 JSON（排序 key）
        """
        if not isinstance(node, dict):
            return str(node)

        obj_id = (node.get("object_type_id") or "").strip()
        u = node.get("unique_identities")
        if obj_id and isinstance(u, dict) and u:
            try:
                return f"uid:{obj_id}:" + json.dumps(u, ensure_ascii=False, sort_keys=True)
            except Exception:
                return f"uid:{obj_id}:" + str(u)

        inst_id = node.get("instance_id")
        if inst_id:
            return f"instance_id:{obj_id}:{inst_id}"

        try:
            return "raw:" + json.dumps(node, ensure_ascii=False, sort_keys=True)
        except Exception:
            return "raw:" + str(node)

    @classmethod
    def _get_current_round(cls, session_id: str, kn_id: str) -> int:
        """
        当前轮次以 retrieval_results 的 round 为准（与 schema 多轮保持一致）。
        """
        try:
            records = cls._session_records[session_id][kn_id].get("retrieval_results", []) or []
            rounds = {r.get("round") for r in records if isinstance(r, dict) and r.get("round")}
            return max(rounds) if rounds else 1
        except Exception:
            return 1

    @classmethod
    def add_semantic_nodes_result(
        cls,
        session_id: str,
        kn_id: str,
        nodes: List[Dict[str, Any]],
        query: Optional[str] = None,
    ) -> int:
        if not session_id or not kn_id:
            return 0
        cls._update_session_access_time(session_id)
        cls._ensure_kn_record(session_id, kn_id)

        current_round = cls._get_current_round(session_id, kn_id)
        entry = {
            "round": current_round,
            "query": query or "",
            "nodes": nodes or [],
        }
        cls._session_records[session_id][kn_id].setdefault("semantic_nodes_results", [])
        cls._session_records[session_id][kn_id]["semantic_nodes_results"].append(entry)
        logger.info(f"会话 {session_id} 的知识网络 {kn_id} 第{current_round}轮保存了 {len(nodes or [])} 个语义 nodes")
        return current_round

    @classmethod
    def get_all_semantic_nodes_union(cls, session_id: str, kn_id: str) -> List[Dict[str, Any]]:
        if (session_id not in cls._session_records) or (kn_id not in cls._session_records[session_id]):
            return []
        cls._update_session_access_time(session_id)

        entries = cls._session_records[session_id][kn_id].get("semantic_nodes_results", []) or []
        # 并集：按 key 去重。若重复，优先保留“分数更高”的版本（若可比），否则保留后写入的版本。
        best: Dict[str, Dict[str, Any]] = {}
        order: List[str] = []

        for entry in entries:
            nodes = entry.get("nodes") if isinstance(entry, dict) else None
            if not isinstance(nodes, list):
                continue
            for n in nodes:
                if not isinstance(n, dict):
                    continue
                k = cls._node_dedup_key(n)
                if k not in best:
                    best[k] = n
                    order.append(k)
                    continue

                prev = best[k]
                # 尝试以 final_score 取更优（否则保持后写入覆盖）
                try:
                    prev_s = float(prev.get("final_score")) if prev.get("final_score") is not None else None
                    cur_s = float(n.get("final_score")) if n.get("final_score") is not None else None
                except Exception:
                    prev_s, cur_s = None, None

                if prev_s is not None and cur_s is not None:
                    if cur_s >= prev_s:
                        best[k] = n
                else:
                    best[k] = n

        return [best[k] for k in order if k in best]

    @classmethod
    def get_previous_semantic_nodes_union(
        cls, session_id: str, kn_id: str, exclude_round: Optional[int]
    ) -> List[Dict[str, Any]]:
        if (session_id not in cls._session_records) or (kn_id not in cls._session_records[session_id]):
            return []
        cls._update_session_access_time(session_id)

        entries = cls._session_records[session_id][kn_id].get("semantic_nodes_results", []) or []
        if exclude_round is None:
            exclude_round = cls._get_current_round(session_id, kn_id)

        # 复用 union 逻辑，但过滤掉 exclude_round
        filtered: List[Dict[str, Any]] = []
        for e in entries:
            if not isinstance(e, dict):
                continue
            if e.get("round") == exclude_round:
                continue
            nodes = e.get("nodes")
            if isinstance(nodes, list) and nodes:
                filtered.append({"nodes": nodes})

        # 把 filtered 伪装成 entries
        best: Dict[str, Dict[str, Any]] = {}
        order: List[str] = []
        for entry in filtered:
            nodes = entry.get("nodes")
            for n in nodes or []:
                if not isinstance(n, dict):
                    continue
                k = cls._node_dedup_key(n)
                if k not in best:
                    best[k] = n
                    order.append(k)
                else:
                    best[k] = n
        return [best[k] for k in order if k in best]

    @classmethod
    def compute_semantic_nodes_return(
        cls,
        session_id: str,
        kn_id: str,
        current_nodes: List[Dict[str, Any]],
        return_union: bool,
        current_round: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        统一计算 nodes 返回：
        - return_union=True：返回并集
        - return_union=False：返回增量（仅当前轮新增的节点）
        """
        if not session_id or not kn_id:
            return current_nodes or []
        if current_round is None:
            current_round = cls._get_current_round(session_id, kn_id)

        if return_union:
            return cls.get_all_semantic_nodes_union(session_id, kn_id)

        prev_union = cls.get_previous_semantic_nodes_union(session_id, kn_id, exclude_round=current_round)
        prev_keys: Set[str] = set(cls._node_dedup_key(n) for n in (prev_union or []) if isinstance(n, dict))

        out: List[Dict[str, Any]] = []
        seen_local: Set[str] = set()
        for n in current_nodes or []:
            if not isinstance(n, dict):
                continue
            k = cls._node_dedup_key(n)
            if k in prev_keys or k in seen_local:
                continue
            seen_local.add(k)
            out.append(n)
        return out


