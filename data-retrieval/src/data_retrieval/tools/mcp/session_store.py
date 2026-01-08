"""MCP Session 存储抽象层，支持内存和 Redis 两种模式。"""

import json
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class SessionStore(ABC):
    """Session 存储抽象基类。"""
    
    @abstractmethod
    def register_identity(self, identity: str) -> None:
        """注册 identity（待绑定 session_id）。"""
        pass
    
    @abstractmethod
    def bind_session(self, session_id: str, identity: Optional[str] = None) -> Optional[str]:
        """绑定 session_id 和 identity，返回绑定的 identity。"""
        pass
    
    @abstractmethod
    def get_identity(self, session_id: str) -> Optional[str]:
        """根据 session_id 获取 identity。"""
        pass
    
    @abstractmethod
    def get_session(self, identity: str) -> Optional[str]:
        """根据 identity 获取 session_id。"""
        pass
    
    @abstractmethod
    def get_any_identity(self) -> Optional[str]:
        """获取任意一个已绑定的 identity（用于单连接场景）。"""
        pass
    
    @abstractmethod
    def cleanup(self, session_id: str) -> None:
        """清理 session 相关数据。"""
        pass
    
    @abstractmethod
    def set_params(self, identity: str, params: Dict[str, Any]) -> None:
        """设置 identity 的参数。"""
        pass
    
    @abstractmethod
    def get_params(self, identity: str) -> Optional[Dict[str, Any]]:
        """获取 identity 的参数。"""
        pass
    
    @abstractmethod
    def clear_params(self, identity: str) -> None:
        """清除 identity 的参数。"""
        pass


class InMemorySessionStore(SessionStore):
    """内存 Session 存储（单进程）。"""
    
    def __init__(self):
        # session_id -> identity 映射
        self._session_to_identity: Dict[str, str] = {}
        # identity -> session_id 映射（None 表示待绑定）
        self._identity_to_session: Dict[str, Optional[str]] = {}
        # identity -> params 映射
        self._identity_params: Dict[str, Dict[str, Any]] = {}
    
    def register_identity(self, identity: str) -> None:
        if identity not in self._identity_to_session:
            self._identity_to_session[identity] = None
            print(f"📝 注册 Identity: {identity}（待绑定 Session）")
    
    def bind_session(self, session_id: str, identity: Optional[str] = None) -> Optional[str]:
        # 如果已绑定，直接返回
        if session_id in self._session_to_identity:
            return self._session_to_identity[session_id]
        
        # 如果没有提供 identity，查找待绑定的
        if not identity:
            for pending_identity, pending_session in self._identity_to_session.items():
                if pending_session is None:
                    identity = pending_identity
                    break
        
        if identity:
            self._session_to_identity[session_id] = identity
            self._identity_to_session[identity] = session_id
            print(f"🔑 绑定 Session [{session_id[:8]}...] <-> Identity: {identity}")
            return identity
        
        return None
    
    def get_identity(self, session_id: str) -> Optional[str]:
        return self._session_to_identity.get(session_id)
    
    def get_session(self, identity: str) -> Optional[str]:
        return self._identity_to_session.get(identity)
    
    def get_any_identity(self) -> Optional[str]:
        """获取任意一个已绑定的 identity（用于单连接场景）。"""
        for identity, session_id in self._identity_to_session.items():
            if session_id is not None:
                return identity
        # 如果没有已绑定的，返回待绑定的
        for identity, session_id in self._identity_to_session.items():
            if session_id is None:
                return identity
        return None
    
    def cleanup(self, session_id: str) -> None:
        if session_id in self._session_to_identity:
            identity = self._session_to_identity.pop(session_id)
            self._identity_to_session.pop(identity, None)
            # 不清除 params，因为可能有多个 session 使用同一个 identity
            print(f"🧹 清理 Session [{session_id[:8]}...] <-> Identity: {identity}")
    
    def set_params(self, identity: str, params: Dict[str, Any]) -> None:
        self._identity_params[identity] = params
    
    def get_params(self, identity: str) -> Optional[Dict[str, Any]]:
        return self._identity_params.get(identity)
    
    def clear_params(self, identity: str) -> None:
        self._identity_params.pop(identity, None)


class RedisSessionStore(SessionStore):
    """Redis Session 存储（多进程/分布式）。"""
    
    # Redis key 前缀
    PREFIX = "mcp:session:"
    PENDING_KEY = "mcp:pending_identities"  # Set 类型
    SESSION_KEY = "mcp:session_to_identity"  # Hash 类型
    IDENTITY_KEY = "mcp:identity_to_session"  # Hash 类型
    PARAMS_KEY = "mcp:identity_params"  # Hash 类型（value 是 JSON）
    
    # 过期时间（秒）
    TTL = 60 * 60 * 24  # 24 小时
    
    def __init__(self, client=None):
        if client:
            self._client = client
        else:
            from data_retrieval.utils.redis_client import RedisConnect
            self._client = RedisConnect.get_client()
    
    def register_identity(self, identity: str) -> None:
        # 检查是否已注册
        if not self._client.hexists(self.IDENTITY_KEY, identity):
            # 添加到待绑定集合
            self._client.sadd(self.PENDING_KEY, identity)
            self._client.expire(self.PENDING_KEY, self.TTL)
            print(f"📝 注册 Identity: {identity}（待绑定 Session）")
    
    def bind_session(self, session_id: str, identity: Optional[str] = None) -> Optional[str]:
        # 如果已绑定，直接返回
        existing = self._client.hget(self.SESSION_KEY, session_id)
        if existing:
            return existing.decode("utf-8") if isinstance(existing, bytes) else existing
        
        # 如果没有提供 identity，从待绑定集合中获取
        if not identity:
            pending = self._client.spop(self.PENDING_KEY)
            if pending:
                identity = pending.decode("utf-8") if isinstance(pending, bytes) else pending
        
        if identity:
            # 双向绑定
            pipe = self._client.pipeline()
            pipe.hset(self.SESSION_KEY, session_id, identity)
            pipe.hset(self.IDENTITY_KEY, identity, session_id)
            pipe.expire(self.SESSION_KEY, self.TTL)
            pipe.expire(self.IDENTITY_KEY, self.TTL)
            # 从待绑定集合中移除（如果还在）
            pipe.srem(self.PENDING_KEY, identity)
            pipe.execute()
            print(f"🔑 绑定 Session [{session_id[:8]}...] <-> Identity: {identity}")
            return identity
        
        return None
    
    def get_identity(self, session_id: str) -> Optional[str]:
        result = self._client.hget(self.SESSION_KEY, session_id)
        return result.decode("utf-8") if isinstance(result, bytes) else result
    
    def get_session(self, identity: str) -> Optional[str]:
        result = self._client.hget(self.IDENTITY_KEY, identity)
        return result.decode("utf-8") if isinstance(result, bytes) else result
    
    def get_any_identity(self) -> Optional[str]:
        """获取任意一个已绑定的 identity。"""
        # 从 IDENTITY_KEY 中获取任意一个
        all_identities = self._client.hkeys(self.IDENTITY_KEY)
        if all_identities:
            identity = all_identities[0]
            return identity.decode("utf-8") if isinstance(identity, bytes) else identity
        # 如果没有已绑定的，尝试从待绑定集合获取
        pending = self._client.srandmember(self.PENDING_KEY)
        if pending:
            return pending.decode("utf-8") if isinstance(pending, bytes) else pending
        return None
    
    def cleanup(self, session_id: str) -> None:
        identity = self.get_identity(session_id)
        if identity:
            pipe = self._client.pipeline()
            pipe.hdel(self.SESSION_KEY, session_id)
            pipe.hdel(self.IDENTITY_KEY, identity)
            pipe.execute()
            print(f"🧹 清理 Session [{session_id[:8]}...] <-> Identity: {identity}")
    
    def set_params(self, identity: str, params: Dict[str, Any]) -> None:
        self._client.hset(self.PARAMS_KEY, identity, json.dumps(params, ensure_ascii=False))
        self._client.expire(self.PARAMS_KEY, self.TTL)
    
    def get_params(self, identity: str) -> Optional[Dict[str, Any]]:
        result = self._client.hget(self.PARAMS_KEY, identity)
        if result:
            data = result.decode("utf-8") if isinstance(result, bytes) else result
            return json.loads(data)
        return None
    
    def clear_params(self, identity: str) -> None:
        self._client.hdel(self.PARAMS_KEY, identity)


# ============== 工厂函数 ==============

_store_instance: Optional[SessionStore] = None

from data_retrieval.settings import get_settings
_settings = get_settings()


def get_session_store() -> SessionStore:
    """
    获取 Session 存储实例（单例）。
    
    通过 settings.MCP_SESSION_STORE 配置：
    - "memory"：使用内存存储（默认）
    - "redis"：使用 Redis 存储
    """
    global _store_instance
    
    if _store_instance is None:
        store_type = _settings.MCP_SESSION_STORE.lower()
        
        if store_type == "redis":
            _store_instance = RedisSessionStore()
            print("📦 使用 Redis Session 存储")
        else:
            _store_instance = InMemorySessionStore()
            print("📦 使用内存 Session 存储")
    
    return _store_instance


def set_session_store(store: SessionStore) -> None:
    """设置自定义 Session 存储实例。"""
    global _store_instance
    _store_instance = store
