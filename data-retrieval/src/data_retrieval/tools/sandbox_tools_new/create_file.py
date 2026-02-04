"""
Create File Tool - Create/upload files to the sandbox environment using RESTful API.
"""
import json
from typing import Optional
from langchain_core.callbacks import CallbackManagerForToolRun, AsyncCallbackManagerForToolRun
from langchain_core.pydantic_v1 import Field

from data_retrieval.logs.logger import logger
from data_retrieval.tools.base import construct_final_answer, async_construct_final_answer
from data_retrieval.errors import SandboxError
from data_retrieval.tools.sandbox_tools_new.base_sandbox_tool import BaseSandboxToolNew, BaseSandboxToolInput
from data_retrieval.utils._common import run_blocking


class CreateFileInput(BaseSandboxToolInput):
    """创建文件工具的输入参数"""
    content: str = Field(
        default="",
        description="文件内容, 如果 result_cache_key 参数不为空，则无需设置该参数"
    )
    filename: str = Field(
        description="要创建的文件名（包含路径）"
    )
    session_type: Optional[str] = Field(
        default="redis",
        description="会话类型, 可选值为: redis, in_memory, 默认值为 redis"
    )
    result_cache_key: Optional[str] = Field(
        default="",
        description="之前工具的结果缓存key，可以将其他工具的结果写入到文件中，有此参数则无需设置 content 参数"
    )


class CreateFileTool(BaseSandboxToolNew):
    """
    创建文件工具，在沙箱环境中创建/上传新文件。

    支持：
    - 直接提供文件内容
    - 从缓存中获取内容（通过 result_cache_key）
    """

    name: str = "create_file"
    description: str = "在沙箱环境中创建新文件，支持文本内容或从缓存中获取内容"
    args_schema: type[BaseSandboxToolInput] = CreateFileInput

    @construct_final_answer
    def _run(
        self,
        filename: str,
        content: str = "",
        title: str = "",
        result_cache_key: str = "",
        run_manager: Optional[CallbackManagerForToolRun] = None
    ):
        try:
            result = run_blocking(self._create_file(
                filename=filename,
                content=content,
                result_cache_key=result_cache_key
            ))
            return result
        except Exception as e:
            logger.error(f"Create file failed: {e}")
            raise SandboxError(reason="创建文件失败", detail=str(e)) from e

    @async_construct_final_answer
    async def _arun(
        self,
        filename: str,
        content: Optional[str] = "",
        result_cache_key: Optional[str] = "",
        title: str = "",
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ):
        try:
            result = await self._create_file(
                filename=filename,
                content=content,
                result_cache_key=result_cache_key
            )

            if self._random_session_id:
                result["session_id"] = self.session_id

            if title:
                result["title"] = title
            else:
                result["title"] = result.get("message", "文件创建完成")

            return result
        except Exception as e:
            logger.error(f"Create file failed: {e}")
            raise SandboxError(reason="创建文件失败", detail=str(e)) from e

    async def _create_file(
        self,
        filename: str,
        content: Optional[str] = "",
        result_cache_key: Optional[str] = ""
    ) -> dict:
        """执行具体的文件创建操作"""
        if not filename:
            raise SandboxError(reason="创建文件失败", detail="filename 参数不能为空")

        # Handle cached content
        if result_cache_key and self.session:
            cached_result = self.session.get_agent_logs(result_cache_key)
            if cached_result:
                cached_data = cached_result.get("data", [])
                logger.info(f"Got data from result_cache_key: {result_cache_key}")

                if cached_data:
                    if isinstance(cached_data, (dict, list)):
                        content = json.dumps(cached_data, ensure_ascii=False)
                    else:
                        content = str(cached_data)

        if not content:
            raise SandboxError(reason="创建文件失败", detail="文件内容不能为空")

        client = self._get_client()

        try:
            # Convert content to bytes for upload
            content_bytes = content.encode("utf-8")

            result = await client.upload_file(
                file_path=filename,
                content=content_bytes
            )

            message = f"文件 {filename} 创建成功，内容前100字符: {content[:100]}"

            return {
                "action": "create_file",
                "result": result,
                "message": message
            }

        except SandboxError:
            raise
        except Exception as e:
            logger.error(f"Create file action failed: {e}")
            raise SandboxError(reason="文件创建失败", detail=str(e)) from e

    @staticmethod
    async def get_api_schema():
        """获取 API Schema"""
        base_schema = await BaseSandboxToolNew.get_api_schema()
        base_schema["post"]["summary"] = "create_file"
        base_schema["post"]["description"] = "在沙箱环境中创建新文件，支持文本内容或从缓存中获取内容"

        # Update request body schema
        base_schema["post"]["requestBody"]["content"]["application/json"]["schema"]["properties"].update({
            "content": {
                "type": "string",
                "description": "文件内容, 如果 result_cache_key 参数不为空，则无需设置该参数"
            },
            "filename": {
                "type": "string",
                "description": "要创建的文件名（包含路径）"
            },
            "session_type": {
                "type": "string",
                "description": "会话类型, 可选值为: redis, in_memory, 默认值为 redis"
            },
            "result_cache_key": {
                "type": "string",
                "description": "之前工具的结果缓存key，可以用于将结果写入到文件中，有此参数则无需设置 content 参数"
            }
        })
        base_schema["post"]["requestBody"]["content"]["application/json"]["schema"]["required"] = ["filename"]

        # Add examples
        base_schema["post"]["requestBody"]["content"]["application/json"]["examples"] = {
            "create_python_file": {
                "summary": "创建 Python 文件",
                "description": "创建包含 Python 代码的文件",
                "value": {
                    "template_id": "python3.11-base",
                    "content": "def fib(n):\n    return n if n <= 1 else fib(n-1) + fib(n-2)",
                    "filename": "fibonacci.py",
                    "session_id": "test_session_123"
                }
            },
            "create_from_cache": {
                "summary": "从缓存创建文件",
                "description": "使用缓存中的数据创建文件",
                "value": {
                    "template_id": "python3.11-base",
                    "filename": "data.json",
                    "result_cache_key": "cached_data_123",
                    "session_id": "test_session_123"
                }
            }
        }

        return base_schema
