"""
Execute Code Tool - Execute code in the sandbox environment using RESTful API.
"""
from typing import Optional, Dict, Any
from langchain_core.callbacks import CallbackManagerForToolRun, AsyncCallbackManagerForToolRun
from langchain_core.pydantic_v1 import Field

from data_retrieval.logs.logger import logger
from data_retrieval.tools.base import construct_final_answer, async_construct_final_answer
from data_retrieval.errors import SandboxError
from data_retrieval.tools.sandbox_tools_new.base_sandbox_tool import BaseSandboxToolNew, BaseSandboxToolInput
from data_retrieval.settings import get_settings
from data_retrieval.utils._common import run_blocking

_settings = get_settings()


class ExecuteCodeInput(BaseSandboxToolInput):
    """执行代码工具的输入参数"""
    code: str = Field(
        description="要执行的代码内容，必须符合 handler 函数格式"
    )
    language: str = Field(
        default="python",
        description="编程语言: python, javascript, shell"
    )
    timeout: int = Field(
        default=30,
        description="执行超时时间（秒）"
    )
    event: Optional[Dict[str, Any]] = Field(
        default=None,
        description="传递给 handler 函数的事件数据"
    )
    sync_execution: Optional[bool] = Field(
        default=None,
        description="是否使用同步执行模式（覆盖工具默认设置）"
    )


class ExecuteCodeTool(BaseSandboxToolNew):
    """
    执行代码工具，在沙箱环境中执行代码。

    支持 Python、JavaScript、Shell 等语言。
    代码需要符合 AWS Lambda handler 格式：

    ```python
    def handler(event):
        # Your code here
        return {"result": "value"}
    ```
    """

    name: str = "execute_code"
    description: str = (
        "在沙箱环境中执行代码。代码需要定义 handler(event) 函数，"
        "通过 event 参数接收输入，通过 return 返回结果。"
        "支持 Python、JavaScript、Shell。"
        "注意：沙箱环境是受限环境，预装了 pandas、numpy 等常用库。"
    )
    args_schema: type[BaseSandboxToolInput] = ExecuteCodeInput

    @construct_final_answer
    def _run(
        self,
        code: str,
        language: str = "python",
        timeout: int = 30,
        event: Optional[Dict[str, Any]] = None,
        sync_execution: Optional[bool] = None,
        title: str = "",
        run_manager: Optional[CallbackManagerForToolRun] = None
    ):
        try:
            result = run_blocking(self._execute_code(
                code=code,
                language=language,
                timeout=timeout,
                event=event,
                sync_execution=sync_execution
            ))
            return result
        except Exception as e:
            logger.error(f"Execute code failed: {e}")
            raise SandboxError(reason="执行代码失败", detail=str(e)) from e

    @async_construct_final_answer
    async def _arun(
        self,
        code: str,
        language: str = "python",
        timeout: int = 30,
        event: Optional[Dict[str, Any]] = None,
        sync_execution: Optional[bool] = None,
        title: str = "",
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ):
        try:
            result = await self._execute_code(
                code=code,
                language=language,
                timeout=timeout,
                event=event,
                sync_execution=sync_execution
            )

            if self._random_user_id:
                result["user_id"] = self.user_id
                result["session_id"] = self._session_id

            if title:
                result["title"] = title
            else:
                result["title"] = result.get("message", "代码执行完成")

            return result
        except Exception as e:
            logger.error(f"Execute code failed: {e}")
            raise SandboxError(reason="执行代码失败", detail=str(e)) from e

    async def _execute_code(
        self,
        code: str,
        language: str,
        timeout: int,
        event: Optional[Dict[str, Any]],
        sync_execution: Optional[bool]
    ) -> dict:
        """执行具体的代码执行操作"""
        if not code:
            raise SandboxError(reason="执行代码失败", detail="code 参数不能为空")

        client = self._get_client()

        # Determine execution mode
        use_sync = sync_execution if sync_execution is not None else self.sync_execution

        try:
            if use_sync:
                # Synchronous execution - wait for result
                result = await client.execute_code_sync(
                    code=code,
                    language=language,
                    timeout=timeout,
                    event=event
                )
            else:
                # Asynchronous execution - submit and poll
                submit_result = await client.execute_code_async(
                    code=code,
                    language=language,
                    timeout=timeout,
                    event=event
                )

                execution_id = submit_result.get("execution_id")
                if not execution_id:
                    raise SandboxError(
                        reason="执行代码失败",
                        detail="未获取到 execution_id"
                    )

                # Wait for execution to complete
                result = await client.wait_for_execution(execution_id)

            # Check for errors in result
            self._check_execution_result(result, "代码执行")

            # Format response
            return {
                "action": "execute_code",
                "result": {
                    "stdout": result.get("stdout", ""),
                    "stderr": result.get("stderr", ""),
                    "return_value": result.get("return_value"),
                    "exit_code": result.get("exit_code", 0),
                    "execution_time": result.get("execution_time"),
                    "status": result.get("status", "COMPLETED")
                },
                "message": "代码执行成功"
            }

        except SandboxError:
            raise
        except Exception as e:
            logger.error(f"Execute code action failed: {e}")
            raise SandboxError(reason="代码执行失败", detail=str(e)) from e

    @staticmethod
    async def get_api_schema():
        """获取 API Schema"""
        base_schema = await BaseSandboxToolNew.get_api_schema()
        base_schema["post"]["summary"] = "execute_code"
        base_schema["post"]["description"] = (
            "在沙箱环境中执行代码。代码需要定义 handler(event) 函数，"
            "通过 event 参数接收输入，通过 return 返回结果。"
            "支持 Python、JavaScript、Shell。"
        )

        # Update request body schema
        base_schema["post"]["requestBody"]["content"]["application/json"]["schema"]["properties"].update({
            "code": {
                "type": "string",
                "description": "要执行的代码内容，需要定义 handler(event) 函数"
            },
            "language": {
                "type": "string",
                "enum": ["python", "javascript", "shell"],
                "description": "编程语言",
                "default": "python"
            },
            "timeout": {
                "type": "integer",
                "description": "执行超时时间（秒）",
                "default": 30
            },
            "event": {
                "type": "object",
                "description": "传递给 handler 函数的事件数据"
            }
        })
        base_schema["post"]["requestBody"]["content"]["application/json"]["schema"]["required"] = ["code"]

        # Add examples
        base_schema["post"]["requestBody"]["content"]["application/json"]["examples"] = {
            "basic_execution": {
                "summary": "基础代码执行",
                "description": "执行简单的 Python 代码",
                "value": {
                    "template_id": "python3.11-base",
                    "code": "def handler(event):\n    return {'msg': 'Hello'}",
                    "language": "python",
                    "event": {"name": "Alice"},
                    "user_id": "user_123"
                }
            },
            "data_analysis": {
                "summary": "数据分析示例",
                "description": "使用 pandas 进行数据分析",
                "value": {
                    "template_id": "python3.11-data",
                    "code": "def handler(event):\n    import pandas as pd\n    return {}",
                    "language": "python",
                    "event": {"data": [{"a": 1}]},
                    "user_id": "user_123"
                }
            }
        }

        return base_schema
