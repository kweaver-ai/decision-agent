from data_retrieval.tools.base import (
    ToolName,
    AFTool
)
from langchain.pydantic_v1 import BaseModel, Field
from data_retrieval.sessions import BaseChatHistorySession, CreateSession
from data_retrieval.tools import async_construct_final_answer, construct_final_answer
from data_retrieval.tools.base import api_tool_decorator
from data_retrieval.settings import get_settings

import json
from fastapi import Body
from data_retrieval.logs.logger import logger

_SETTINGS = get_settings()


class GetToolCacheInput(BaseModel):
    cache_key: str = Field(..., description="工具缓存 key")


class GetToolCacheTool(AFTool):
    """
    获取工具缓存
    """
    name: str = ToolName.from_get_tool_cache.value
    description: str = "根据工具的缓存 key 获取工具缓存，如果获取出错，则需要重新调用其他工具获取数据，一般情况下不需要调用"
    parameters: BaseModel = GetToolCacheInput
    session_type: str = "redis"
    session: BaseChatHistorySession = None
    max_cache_size: int = _SETTINGS.CACHE_SIZE_LIMIT

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.session:
            self.session = CreateSession(self.session_type)

    def _get_tool_cache(self, cache_key: str) -> dict:
        """获取工具缓存并处理大小限制

        Returns:
            dict: 包含 "output" key 的字典，兼容 construct_final_answer 装饰器。
                  正常情况返回原始 dict/list；超限时返回截断后的字符串。
        """
        tool_res = self.session.get_agent_logs(cache_key)
        res_str = json.dumps(tool_res, ensure_ascii=False)
        if len(res_str) > self.max_cache_size:
            # 如果超过限制，则需要截取一部分, CACHE_SIZE_LIMIT 的 前 80% 和后 20%
            truncated = (
                res_str[:int(self.max_cache_size * 0.8)] +
                f"\n...实际长度为 {len(res_str)}, 中间省去 {len(res_str) - self.max_cache_size}...\n" +
                res_str[-int(self.max_cache_size * 0.2):]
            )
            return {"output": truncated}
        return {"output": tool_res}

    @construct_final_answer
    def _run(self, cache_key: str) -> str:
        """
        获取工具缓存
        """
        return self._get_tool_cache(cache_key)

    @async_construct_final_answer
    async def _arun(self, cache_key: str) -> str:
        """
        异步获取工具缓存
        """
        return self._get_tool_cache(cache_key)

    @classmethod
    @api_tool_decorator
    async def as_async_api_cls(
        cls,
        params: dict = Body(...),
        stream: bool = False,
        mode: str = "http"
    ):
        """
        异步获取工具缓存
        """
        logger.info(f"get_tool_cache as_async_api_cls params: {params}")
        cache_key = params.get('cache_key', '')
        session_type = params.get('session_type', 'redis')
        max_cache_size = params.get('max_cache_size', _SETTINGS.CACHE_SIZE_LIMIT)

        tool = cls(
            session_type=session_type,
            max_cache_size=max_cache_size
        )

        return await tool._arun(cache_key)

    @staticmethod
    async def get_api_schema() -> dict:
        """
        获取工具缓存的 API 文档
        """
        return {
            "post": {
                "summary": ToolName.from_get_tool_cache.value,
                "description": "根据工具的缓存 key 获取工具缓存，如果获取出错，则需要重新调用其他工具获取数据",
                "parameters": [
                    {
                        "name": "cache_key",
                        "in": "query",
                        "description": "工具缓存 key",
                        "schema": {
                            "type": "string",
                        },
                    },
                    {
                        "name": "session_type",
                        "in": "query",
                        "description": "会话类型",
                        "schema": {
                            "type": "string",
                        },
                    },
                ],
            }
        }
