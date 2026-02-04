"""
List Files Tool - List files in the sandbox environment using RESTful API.
"""
from typing import Optional
from langchain_core.callbacks import CallbackManagerForToolRun, AsyncCallbackManagerForToolRun
from langchain_core.pydantic_v1 import Field

from data_retrieval.logs.logger import logger
from data_retrieval.tools.base import construct_final_answer, async_construct_final_answer
from data_retrieval.errors import SandboxError
from data_retrieval.tools.sandbox_tools_new.base_sandbox_tool import BaseSandboxToolNew, BaseSandboxToolInput
from data_retrieval.utils._common import run_blocking


class ListFilesInput(BaseSandboxToolInput):
    """列出文件工具的输入参数"""
    path: Optional[str] = Field(
        default=None,
        description="可选，指定目录路径（相对于 workspace 根目录），不指定则列出所有文件"
    )
    limit: int = Field(
        default=1000,
        description="最大返回文件数 (1-10000)"
    )


class ListFilesTool(BaseSandboxToolNew):
    """
    列出文件工具，列出沙箱环境中的所有文件和目录。

    支持：
    - 列出所有文件
    - 按目录路径筛选
    - 限制返回数量
    """

    name: str = "list_files"
    description: str = "列出沙箱环境中的所有文件和目录"
    args_schema: type[BaseSandboxToolInput] = ListFilesInput

    @construct_final_answer
    def _run(
        self,
        path: Optional[str] = None,
        limit: int = 1000,
        title: str = "",
        run_manager: Optional[CallbackManagerForToolRun] = None
    ):
        try:
            result = run_blocking(self._list_files(path=path, limit=limit))
            return result
        except Exception as e:
            logger.error(f"List files failed: {e}")
            raise SandboxError(reason="列出文件失败", detail=str(e)) from e

    @async_construct_final_answer
    async def _arun(
        self,
        path: Optional[str] = None,
        limit: int = 1000,
        title: str = "",
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ):
        try:
            result = await self._list_files(path=path, limit=limit)

            if self._random_user_id:
                result["user_id"] = self.user_id
                result["session_id"] = self._session_id

            if title:
                result["title"] = title
            else:
                result["title"] = result.get("message", "文件列表获取完成")

            return result
        except Exception as e:
            logger.error(f"List files failed: {e}")
            raise SandboxError(reason="列出文件失败", detail=str(e)) from e

    async def _list_files(
        self,
        path: Optional[str] = None,
        limit: int = 1000
    ) -> dict:
        """执行具体的文件列表操作"""
        client = self._get_client()

        try:
            result = await client.list_files(path=path, limit=limit)

            # Format response
            files = result if isinstance(result, list) else result.get("files", [])

            return {
                "action": "list_files",
                "result": {
                    "files": files,
                    "count": len(files) if isinstance(files, list) else 0,
                    "path": path or "/"
                },
                "message": "文件列表获取成功"
            }

        except SandboxError:
            raise
        except Exception as e:
            logger.error(f"List files action failed: {e}")
            raise SandboxError(reason="文件列表获取失败", detail=str(e)) from e

    @staticmethod
    async def get_api_schema():
        """获取 API Schema"""
        base_schema = await BaseSandboxToolNew.get_api_schema()
        base_schema["post"]["summary"] = "list_files"
        base_schema["post"]["description"] = "列出沙箱环境中的所有文件和目录"

        # Update request body schema
        base_schema["post"]["requestBody"]["content"]["application/json"]["schema"]["properties"].update({
            "path": {
                "type": "string",
                "description": "可选，指定目录路径（相对于 workspace 根目录），不指定则列出所有文件"
            },
            "limit": {
                "type": "integer",
                "description": "最大返回文件数 (1-10000)",
                "default": 1000,
                "minimum": 1,
                "maximum": 10000
            }
        })
        base_schema["post"]["requestBody"]["content"]["application/json"]["schema"]["required"] = []

        # Add examples
        base_schema["post"]["requestBody"]["content"]["application/json"]["examples"] = {
            "list_all_files": {
                "summary": "列出所有文件",
                "description": "列出沙箱环境中的所有文件和目录",
                "value": {
                    "template_id": "python3.11-base",
                    "user_id": "user_123"
                }
            },
            "list_directory": {
                "summary": "列出指定目录",
                "description": "列出指定目录下的文件",
                "value": {
                    "template_id": "python3.11-base",
                    "path": "src/",
                    "limit": 100,
                    "user_id": "user_123"
                }
            }
        }

        return base_schema
