"""Redis 客户端连接工具类。"""

import redis
from redis.sentinel import Sentinel
from typing import Optional

from data_retrieval.settings import get_settings


class RedisConnect:
    """Redis 连接管理器，支持主从模式和哨兵模式。"""
    
    _instance: Optional[redis.Redis] = None
    
    def __init__(self):
        settings = get_settings()
        self.redis_cluster_mode = settings.REDISCLUSTERMODE
        self.db = settings.REDIS_DB
        self.master_name = settings.SENTINELMASTER
        self.sentinel_user_name = settings.SENTINELUSER

        self.host = settings.REDISHOST
        self.sentinel_host = settings.REDIS_SENTINEL_HOST

        self.port = settings.REDISPORT
        self.sentinel_port = settings.REDIS_SENTINEL_PORT

        self.password = settings.REDIS_PASSWORD
        self.sentinel_password = settings.SENTINELPASS

    def connect(self) -> redis.Redis:
        """创建 Redis 连接。"""
        if self.redis_cluster_mode == "master-slave":
            pool = redis.ConnectionPool(
                host=self.host,
                port=self.port,
                password=self.password,
                db=self.db,
            )
            client = redis.StrictRedis(connection_pool=pool)
            return client
        
        if self.redis_cluster_mode == "sentinel":
            sentinel = Sentinel(
                [(self.sentinel_host, self.sentinel_port)],
                password=self.sentinel_password,
                sentinel_kwargs={
                    "password": self.sentinel_password,
                    "username": self.sentinel_user_name
                }
            )
            client = sentinel.master_for(
                self.master_name,
                password=self.sentinel_password,
                username=self.sentinel_user_name,
                db=self.db
            )
            return client
        
        raise ValueError(f"不支持的 Redis 集群模式: {self.redis_cluster_mode}")
    
    @classmethod
    def get_client(cls) -> redis.Redis:
        """获取单例 Redis 客户端。"""
        if cls._instance is None:
            cls._instance = cls().connect()
        return cls._instance
