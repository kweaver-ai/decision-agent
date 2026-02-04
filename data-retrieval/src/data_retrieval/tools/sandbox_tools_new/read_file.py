"""
Read File Tool - Read/download files from the sandbox environment using RESTful API.
"""
import json
import traceback
from typing import Optional
from langchain_core.callbacks import CallbackManagerForToolRun, AsyncCallbackManagerForToolRun
from langchain_core.pydantic_v1 import Field

from data_retrieval.logs.logger import logger
from data_retrieval.tools.base import construct_final_answer, async_construct_final_answer
from data_retrieval.errors import SandboxError
from data_retrieval.tools.sandbox_tools_new.base_sandbox_tool import BaseSandboxToolNew, BaseSandboxToolInput
from data_retrieval.utils._common import run_blocking


class ReadFileInput(BaseSandboxToolInput):
    """读取文件工具的输入参数"""
    filename: str = Field(
        description="要读取的文件名（包含路径）"
    )
    session_type: Optional[str] = Field(
        default="redis",
        description="会话类型, 可选值为: redis, in_memory, 默认值为 redis"
    )


class ReadFileTool(BaseSandboxToolNew):
    """
    读取文件工具，从沙箱环境中读取/下载文件内容。

    支持：
    - 读取文本文件
    - 读取二进制文件
    - 自动缓存读取结果（通过 result_cache_key）
    """

    name: str = "read_file"
    description: str = "读取沙箱环境中的文件内容，支持文本文件和二进制文件"
    args_schema: type[BaseSandboxToolInput] = ReadFileInput

    @construct_final_answer
    def _run(
        self,
        filename: str,
        title: str = "",
        run_manager: Optional[CallbackManagerForToolRun] = None
    ):
        try:
            result = run_blocking(self._read_file(filename))
            return result
        except Exception as e:
            logger.error(f"Read file failed: {e}")
            raise SandboxError(reason="读取文件失败", detail=str(e)) from e

    @async_construct_final_answer
    async def _arun(
        self,
        filename: str,
        title: str = "",
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ):
        try:
            result = await self._read_file(filename)

            if self._random_session_id:
                result["session_id"] = self.session_id

            if title:
                result["title"] = title
            else:
                result["title"] = result.get("output", {}).get("message", "文件读取完成")

            return result
        except Exception as e:
            logger.error(f"Read file failed: {e}")
            raise SandboxError(reason="读取文件失败", detail=str(e)) from e

    async def _read_file(self, filename: str) -> dict:
        """执行具体的文件读取操作"""
        if not filename:
            raise SandboxError(reason="读取文件失败", detail="filename 参数不能为空")

        client = self._get_client()

        try:
            # Download file content as bytes
            content_bytes = await client.download_file(filename)

            # Try to decode as text
            is_binary = False
            try:
                content = content_bytes.decode("utf-8")
            except UnicodeDecodeError:
                # Binary file - return as base64 or indicate it's binary
                is_binary = True
                content = f"[Binary file, size: {len(content_bytes)} bytes]"

            size = len(content_bytes)

            # Check file size limit (50MB)
            if size >= 50 * 1024 * 1024:
                raise SandboxError(reason="读取文件失败", detail="文件过大，单个文件不超过50MB")

            logger.info(f"文件大小: {size} bytes, is_binary: {is_binary}")

            res_output = {
                "action": "read_file",
                "result": {
                    "content(head100)": content[:100] if not is_binary else "[Binary]",
                    "is_binary": is_binary,
                    "size": size
                },
                "message": f"文件 {filename} 读取成功，前100字符(如有): {content[:100] if not is_binary else '[Binary]'}"
            }

            # Cache result if session is available
            if self.session and not is_binary:
                try:
                    cache_data = json.loads(content)
                    self.session.add_agent_logs(
                        self._result_cache_key,
                        {"data": cache_data}
                    )
                    res_output["result_cache_key"] = self._result_cache_key
                    logger.info(f"Cached result with key: {self._result_cache_key}")
                except json.JSONDecodeError:
                    # Not JSON, cache as plain text
                    self.session.add_agent_logs(
                        self._result_cache_key,
                        {"data": content}
                    )
                    res_output["result_cache_key"] = self._result_cache_key
                    logger.info(f"Cached text result with key: {self._result_cache_key}")
                except Exception as e:
                    traceback.format_exc()
                    logger.warning(f"Failed to cache result: {str(e)}")

            return {"output": res_output}

        except SandboxError:
            raise
        except Exception as e:
            logger.error(f"Read file action failed: {e}")
            raise SandboxError(reason="文件读取失败", detail=str(e)) from e

    @staticmethod
    async def get_api_schema():
        """获取 API Schema"""
        base_schema = await BaseSandboxToolNew.get_api_schema()
        base_schema["post"]["summary"] = "read_file"
        base_schema["post"]["description"] = "读取沙箱环境中的文件内容，支持文本文件和二进制文件"

        # Update request body schema
        base_schema["post"]["requestBody"]["content"]["application/json"]["schema"]["properties"].update({
            "filename": {
                "type": "string",
                "description": "要读取的文件名（包含路径）"
            },
            "session_type": {
                "type": "string",
                "description": "会话类型, 可选值为: redis, in_memory, 默认值为 redis"
            }
        })
        base_schema["post"]["requestBody"]["content"]["application/json"]["schema"]["required"] = ["filename"]

        # Add examples
        base_schema["post"]["requestBody"]["content"]["application/json"]["examples"] = {
            "read_python_file": {
                "summary": "读取 Python 文件",
                "description": "读取 Python 源代码文件",
                "value": {
                    "template_id": "python3.11-base",
                    "filename": "hello.py",
                    "session_id": "test_session_123"
                }
            },
            "read_json_file": {
                "summary": "读取 JSON 文件",
                "description": "读取 JSON 数据文件并自动缓存",
                "value": {
                    "template_id": "python3.11-base",
                    "filename": "data.json",
                    "session_id": "test_session_123"
                }
            }
        }

        return base_schema
