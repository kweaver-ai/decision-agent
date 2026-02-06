"""
Terminate Session Tool - Terminate sandbox session using RESTful API.

This tool replaces the old CloseSandboxTool functionality.
"""
from typing import Optional
from langchain_core.callbacks import CallbackManagerForToolRun, AsyncCallbackManagerForToolRun

from data_retrieval.logs.logger import logger
from data_retrieval.tools.base import construct_final_answer, async_construct_final_answer
from data_retrieval.errors import SandboxError
from data_retrieval.tools.sandbox_tools_new.base_sandbox_tool import BaseSandboxToolNew, BaseSandboxToolInput
from data_retrieval.utils._common import run_blocking


class TerminateSessionInput(BaseSandboxToolInput):
    """终止会话工具的输入参数"""
    # 目前不需要额外参数，但保留结构以便未来扩展
    pass


class TerminateSessionTool(BaseSandboxToolNew):
    """
    终止会话工具，终止沙箱会话并清理资源。

    行为：
    1. 销毁容器
    2. 删除 S3 工作区文件
    3. 更新会话状态为 terminated
    4. 保留数据库记录

    注意：这是软终止，会保留记录用于审计。如需硬删除，请使用 delete_session API。
    """

    name: str = "terminate_session"
    description: str = "终止沙箱会话，清理工作区资源。保留会话记录用于审计。"
    args_schema: type[BaseSandboxToolInput] = TerminateSessionInput

    @construct_final_answer
    def _run(
        self,
        title: str = "",
        run_manager: Optional[CallbackManagerForToolRun] = None
    ):
        try:
            result = run_blocking(self._terminate_session())

            if title:
                result["title"] = title
            else:
                result["title"] = result.get("message", "会话终止完成")

            return result
        except Exception as e:
            logger.error(f"Terminate session failed: {e}")
            raise SandboxError(reason="终止会话失败", detail=str(e)) from e

    @async_construct_final_answer
    async def _arun(
        self,
        title: str = "",
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ):
        try:
            result = await self._terminate_session()

            if self._random_user_id:
                result["user_id"] = self.user_id
                result["session_id"] = self._session_id

            if title:
                result["title"] = title
            else:
                result["title"] = result.get("message", "会话终止完成")

            return result
        except Exception as e:
            logger.error(f"Terminate session failed: {e}")
            raise SandboxError(reason="终止会话失败", detail=str(e)) from e

    async def _terminate_session(self) -> dict:
        """执行具体的会话终止操作"""
        client = self._get_client()

        try:
            result = await client.terminate_session()

            # Close the HTTP client
            await client.close()

            # Clear the client instance
            self._client = None

            return {
                "action": "terminate_session",
                "result": {
                    "user_id": self.user_id,
                    "session_id": self._session_id,
                    "status": result.get("status", "terminated")
                },
                "message": "会话已终止，工作区清理成功"
            }

        except SandboxError:
            raise
        except Exception as e:
            logger.error(f"Terminate session action failed: {e}")
            raise SandboxError(reason="会话终止失败", detail=str(e)) from e

    @staticmethod
    async def get_api_schema():
        """获取 API Schema"""
        base_schema = await BaseSandboxToolNew.get_api_schema()
        base_schema["post"]["summary"] = "terminate_session"
        base_schema["post"]["description"] = (
            "终止沙箱会话，清理工作区资源。"
            "这是软终止操作，会销毁容器和工作区文件，但保留会话记录用于审计。"
        )

        # Update request body schema - user_id required for termination
        base_schema["post"]["requestBody"]["content"]["application/json"]["schema"]["required"] = ["user_id"]

        # Add examples
        base_schema["post"]["requestBody"]["content"]["application/json"]["examples"] = {
            "terminate_session": {
                "summary": "终止会话",
                "description": "终止指定用户的沙箱会话",
                "value": {
                    "template_id": "python-basic",
                    "user_id": "user_123"
                }
            }
        }

        return base_schema
