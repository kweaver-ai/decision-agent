# -*- coding:utf-8 -*-
"""Agent 实例管理器 - 管理 agent_run_id 与 DolphinAgent 实例的映射

支持内存优先 + 文件兜底的二级存储策略：
- 写入时同时写内存和文件（pickle 序列化）
- 读取时先查内存，内存没有则查文件，文件有则回填内存
- 删除时同时删内存和文件
- 内存 30 分钟过期自动清理，文件暂不过期
"""

import os
import pickle
from typing import Dict, Optional, Tuple, TYPE_CHECKING
from threading import Lock
import time

from app.common.stand_log import StandLogger

if TYPE_CHECKING:
    from dolphin.sdk.agent.dolphin_agent import DolphinAgent
    from app.logic.agent_core_logic_v2.agent_core_v2 import AgentCoreV2


class AgentInstanceManager:
    """管理 agent_run_id 到 Agent 实例的映射（单例）

    二级存储策略：
    - L1: 内存 Dict（快速访问，30分钟过期）
    - L2: 文件 pickle（持久化，暂不过期）
    """

    _instance: Optional["AgentInstanceManager"] = None
    _lock: Lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._init()
        return cls._instance

    def _init(self):
        # agent_run_id -> (DolphinAgent, AgentCoreV2, timestamp)
        self._instances: Dict[str, Tuple] = {}
        self._instance_lock = Lock()
        # 实例过期时间（秒）
        self._expire_seconds = 30 * 60  # 30分钟
        # 文件持久化目录
        self._storage_dir = os.path.join("./data", "agent_instances")
        os.makedirs(self._storage_dir, exist_ok=True)
        # 启动后台清理线程
        self._start_cleanup_thread()

    def _start_cleanup_thread(self):
        """启动后台清理线程"""
        import threading

        def cleanup_loop():
            while True:
                time.sleep(60)  # 每分钟清理一次
                try:
                    self.cleanup_expired()
                except Exception:
                    pass  # 忽略清理异常

        thread = threading.Thread(
            target=cleanup_loop, daemon=True, name="agent-instance-cleanup"
        )
        thread.start()

    # ========== 文件持久化私有方法 ==========

    def _get_file_path(self, agent_run_id: str) -> str:
        """获取 agent_run_id 对应的文件路径"""
        # 对 agent_run_id 做安全处理，避免路径注入
        safe_id = agent_run_id.replace("/", "_").replace("\\", "_")
        return os.path.join(self._storage_dir, f"{safe_id}.pkl")

    def _save_to_file(
        self,
        agent_run_id: str,
        agent: "DolphinAgent",
        agent_core: "AgentCoreV2",
        timestamp: float,
    ) -> None:
        """将实例数据序列化到文件

        Args:
            agent_run_id: Agent 运行 ID
            agent: DolphinAgent 实例
            agent_core: AgentCoreV2 实例
            timestamp: 注册时间戳
        """
        file_path = self._get_file_path(agent_run_id)
        try:
            data = (agent, agent_core, timestamp)
            with open(file_path, "wb") as f:
                pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception as e:
            StandLogger.error(
                f"Failed to save agent instance to file: "
                f"agent_run_id={agent_run_id}, error={e}"
            )

    def _load_from_file(
        self, agent_run_id: str
    ) -> Optional[Tuple]:
        """从文件加载实例数据

        Args:
            agent_run_id: Agent 运行 ID

        Returns:
            (DolphinAgent, AgentCoreV2, timestamp) 或 None
        """
        file_path = self._get_file_path(agent_run_id)
        if not os.path.exists(file_path):
            return None

        try:
            with open(file_path, "rb") as f:
                data = pickle.load(f)
            # 验证数据结构
            if not isinstance(data, tuple) or len(data) != 3:
                StandLogger.error(
                    f"Invalid data structure in file: "
                    f"agent_run_id={agent_run_id}, removing corrupted file"
                )
                self._remove_file(agent_run_id)
                return None
            return data
        except Exception as e:
            StandLogger.error(
                f"Failed to load agent instance from file: "
                f"agent_run_id={agent_run_id}, error={e}"
            )
            # 文件损坏，删除并返回 None
            self._remove_file(agent_run_id)
            return None

    def _remove_file(self, agent_run_id: str) -> None:
        """安全删除实例文件

        Args:
            agent_run_id: Agent 运行 ID
        """
        file_path = self._get_file_path(agent_run_id)
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            StandLogger.error(
                f"Failed to remove agent instance file: "
                f"agent_run_id={agent_run_id}, error={e}"
            )

    # ========== 公共方法 ==========

    def register(
        self,
        agent_run_id: str,
        agent: "DolphinAgent",
        agent_core: "AgentCoreV2",
    ) -> None:
        """注册 Agent 实例（同时写内存和文件）

        Args:
            agent_run_id: Agent 运行 ID
            agent: DolphinAgent 实例
            agent_core: AgentCoreV2 实例
        """
        current_time = time.time()
        with self._instance_lock:
            self._instances[agent_run_id] = (agent, agent_core, current_time)
        # 写文件（在锁外执行，避免 IO 阻塞）
        self._save_to_file(agent_run_id, agent, agent_core, current_time)

    def get(
        self, agent_run_id: str
    ) -> Optional[Tuple["DolphinAgent", "AgentCoreV2"]]:
        """获取 Agent 实例（内存优先，文件兜底）

        查找策略：
        1. 先查内存，命中且未过期则直接返回
        2. 内存未命中（不存在或已过期），尝试从文件加载
        3. 文件命中则回填内存并返回
        4. 都没有则返回 None

        Args:
            agent_run_id: Agent 运行 ID

        Returns:
            (DolphinAgent, AgentCoreV2) 或 None
        """
        with self._instance_lock:
            data = self._instances.get(agent_run_id)
            if data is not None:
                agent, agent_core, timestamp = data
                # 检查是否过期
                if time.time() - timestamp > self._expire_seconds:
                    del self._instances[agent_run_id]
                else:
                    return (agent, agent_core)

        # 内存没有，尝试从文件加载
        result = self._load_from_file(agent_run_id)
        if result is not None:
            agent, agent_core, timestamp = result
            # 回填内存（使用当前时间作为新 timestamp）
            with self._instance_lock:
                self._instances[agent_run_id] = (agent, agent_core, time.time())
            return (agent, agent_core)
        return None

    def remove(self, agent_run_id: str) -> None:
        """移除 Agent 实例（同时删内存和文件）

        Args:
            agent_run_id: Agent 运行 ID
        """
        with self._instance_lock:
            self._instances.pop(agent_run_id, None)
        # 删文件（在锁外执行）
        self._remove_file(agent_run_id)

    def cleanup_expired(self) -> None:
        """清理过期的内存实例（文件暂不清理）"""
        current_time = time.time()
        with self._instance_lock:
            expired_ids = [
                run_id
                for run_id, (_, _, ts) in self._instances.items()
                if current_time - ts > self._expire_seconds
            ]
            for run_id in expired_ids:
                del self._instances[run_id]


# 全局单例
agent_instance_manager = AgentInstanceManager()
