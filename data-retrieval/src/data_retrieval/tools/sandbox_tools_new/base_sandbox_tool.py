"""
Base Sandbox Tool for the new RESTful API.

This module provides the base class for all sandbox tools that use the new
sandbox control plane API instead of the SDK.
"""
import uuid
from typing import Optional
from langchain_core.pydantic_v1 import PrivateAttr, BaseModel, Field
from fastapi import Body

from data_retrieval.logs.logger import logger
from data_retrieval.sessions import BaseChatHistorySession, CreateSession
from data_retrieval.tools.base import AFTool, api_tool_decorator
from data_retrieval.settings import get_settings
from data_retrieval.errors import SandboxError
from data_retrieval.utils._common import is_valid_url
from data_retrieval.tools.sandbox_tools_new.client import SandboxAPIClient


_settings = get_settings()


class BaseSandboxToolInput(BaseModel):
    """基础沙箱工具输入参数"""
    title: str = Field(
        default="",
        description="对于当前操作的简单描述，便于用户理解"
    )


class BaseSandboxToolNew(AFTool):
    """
    基础沙箱工具类，使用新的 RESTful API。

    与旧版 BaseSandboxTool 的区别：
    - 使用 SandboxAPIClient 进行 HTTP 调用，而非 SDK
    - 需要 template_id 参数
    - 支持配置 sync/async 执行模式
    - 自动创建会话（如果不存在）
    """

    session_id: str = ""
    server_url: str = _settings.SANDBOX_URL
    template_id: str = "python-basic"  # Default template for session creation
    session: Optional[BaseChatHistorySession] = None
    session_type: Optional[str] = "redis"
    sync_execution: bool = True  # Use sync execution by default

    _client: Optional[SandboxAPIClient] = PrivateAttr(None)
    _random_session_id: bool = PrivateAttr(False)
    _result_cache_key: str = PrivateAttr("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Generate random session_id if not provided
        if not self.session_id:
            self.session_id = str(uuid.uuid4())
            self._random_session_id = True
            logger.info(f"Randomly generated session_id: {self.session_id}")

        logger.info(f"BaseSandboxToolNew initialized with session_id: {self.session_id}")
        logger.info(f"BaseSandboxToolNew initialized with template_id: {self.template_id}")
        logger.info(f"BaseSandboxToolNew initialized with session_type: {self.session_type}")

        # Initialize chat history session for caching
        self.session = CreateSession(self.session_type)

        # Validate server URL
        if not is_valid_url(self.server_url):
            self.server_url = _settings.SANDBOX_URL
            logger.warning(f"Invalid server URL, using default: {_settings.SANDBOX_URL}")

        # Generate result cache key
        self._result_cache_key = f"sandbox_result_{self.session_id}_{uuid.uuid4().hex[:8]}"

    def _get_client(self) -> SandboxAPIClient:
        """获取或创建 API 客户端实例"""
        if self._client is None:
            if not self.template_id:
                raise SandboxError(
                    reason="初始化失败",
                    detail="template_id 参数不能为空"
                )

            self._client = SandboxAPIClient(
                server_url=self.server_url,
                template_id=self.template_id,
                session_id=self.session_id
            )
        return self._client

    def _check_execution_result(self, result: dict, operation_name: str):
        """检查执行结果，判断是否有错误"""
        if not isinstance(result, dict):
            return

        # Check status
        status = result.get("status", "").upper()
        if status in ["FAILED", "CRASHED"]:
            error_msg = result.get("error_message", "")
            stderr = result.get("stderr", "")
            detail = error_msg or stderr or "执行失败"
            logger.error(f"{operation_name} 失败: status={status}, detail={detail}")
            raise SandboxError(
                reason=f"{operation_name}失败",
                detail=detail
            )

        if status == "TIMEOUT":
            logger.error(f"{operation_name} 超时")
            raise SandboxError(
                reason=f"{operation_name}超时",
                detail="执行超过最大等待时间"
            )

        # Check stderr (warning only)
        stderr = result.get("stderr", "")
        if stderr and stderr.strip():
            logger.warning(f"{operation_name} 有错误输出: {stderr}")

        # Check exit_code
        exit_code = result.get("exit_code")
        if exit_code is not None and exit_code != 0:
            error_msg = f"{operation_name} 返回非零退出码: {exit_code}"
            if stderr:
                error_msg += f", 错误信息: {stderr}"
            logger.error(error_msg)
            raise SandboxError(
                reason=f"{operation_name}失败",
                detail=f"退出码: {exit_code}, 错误信息: {stderr}"
            )

        # Check error_message field
        error_message = result.get("error_message")
        if error_message:
            logger.error(f"{operation_name} 返回错误: {error_message}")
            raise SandboxError(
                reason=f"{operation_name}失败",
                detail=str(error_message)
            )

    @classmethod
    @api_tool_decorator
    async def as_async_api_cls(
        cls,
        params: dict = Body(...),
        stream: bool = False,
        mode: str = "http"
    ):
        """异步API调用方法，由子类继承使用"""
        server_url = params.get("server_url", _settings.SANDBOX_URL)
        session_id = params.get("session_id", "")
        session_type = params.get("session_type", "redis")
        template_id = params.get("template_id", "")
        sync_execution = params.get("sync_execution", True)

        logger.info(f"as_async_api_cls params: {params}")

        tool = cls(
            server_url=server_url,
            session_id=session_id,
            session_type=session_type,
            template_id=template_id,
            sync_execution=sync_execution
        )

        # 移除通用参数，保留工具特定参数
        tool_params = {
            k: v for k, v in params.items()
            if k not in ["server_url", "session_id", "session_type", "template_id", "sync_execution"]
        }

        # invoke tool
        res = await tool.ainvoke(tool_params)
        return res

    @staticmethod
    async def get_api_schema():
        """获取API Schema的基类方法，包含共同参数"""
        return {
            "post": {
                "summary": "Base Sandbox Tool (New API)",
                "description": "基础沙箱工具（使用新的 RESTful API），子类应该重写此方法提供具体的API Schema",
                "parameters": [
                    {
                        "name": "stream",
                        "in": "query",
                        "description": "是否流式返回",
                        "schema": {
                            "type": "boolean",
                            "default": False
                        },
                    },
                    {
                        "name": "mode",
                        "in": "query",
                        "description": "请求模式",
                        "schema": {
                            "type": "string",
                            "enum": ["http", "sse"],
                            "default": "http"
                        },
                    }
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "server_url": {
                                        "type": "string",
                                        "description": "可选，沙箱服务器URL，默认使用配置文件中的 SANDBOX_URL",
                                        "default": _settings.SANDBOX_URL
                                    },
                                    "session_id": {
                                        "type": "string",
                                        "description": "沙箱会话ID，如不提供则自动生成"
                                    },
                                    "template_id": {
                                        "type": "string",
                                        "description": "沙箱模板ID，用于创建会话",
                                        "default": "python-basic"
                                    },
                                    "sync_execution": {
                                        "type": "boolean",
                                        "description": "是否使用同步执行模式",
                                        "default": True
                                    },
                                    "timeout": {
                                        "type": "number",
                                        "description": "超时时间（秒）",
                                        "default": 120
                                    },
                                    "title": {
                                        "type": "string",
                                        "description": "对于当前操作的简单描述，便于用户理解"
                                    }
                                },
                                "required": []
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Successful operation",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "result": {
                                            "type": "object",
                                            "description": "操作结果, 包含标准输出、标准错误输出、返回值"
                                        },
                                        "message": {
                                            "type": "string",
                                            "description": "操作状态消息"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "400": {
                        "description": "Bad request",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {
                                            "type": "string",
                                            "description": "错误信息"
                                        },
                                        "detail": {
                                            "type": "string",
                                            "description": "详细错误信息"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
