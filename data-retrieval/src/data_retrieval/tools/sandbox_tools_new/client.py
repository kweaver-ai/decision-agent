"""
Sandbox API Client - HTTP client for the new sandbox RESTful API (v2.1.0)

This client handles all HTTP interactions with the sandbox control plane API,
including session management, code execution, and file operations.
"""
import asyncio
from typing import Optional, Dict, Any
import httpx

from data_retrieval.logs.logger import logger
from data_retrieval.errors import SandboxError


class SandboxAPIClient:
    """
    HTTP client for interacting with the new Sandbox Control Plane API.

    Handles:
    - Session lifecycle (create, get, terminate)
    - Code execution (sync and async modes)
    - File operations (list, upload, download)
    """

    DEFAULT_TIMEOUT = 300  # seconds
    DEFAULT_EXECUTION_TIMEOUT = 30  # seconds

    def __init__(
        self,
        server_url: str,
        template_id: str,
        session_id: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT
    ):
        """
        Initialize the sandbox API client.

        Args:
            server_url: Base URL of the sandbox API server
            template_id: Template ID for session creation
            session_id: Optional existing session ID
            timeout: Session timeout in seconds
        """
        self.server_url = server_url.rstrip("/")
        self.template_id = template_id
        self.session_id = session_id
        self.timeout = timeout
        self._session_created = False
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the async HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.server_url,
                timeout=httpx.Timeout(self.timeout + 60)  # Extra buffer for network
            )
        return self._client

    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    def _build_url(self, path: str) -> str:
        """Build full URL from path."""
        return f"{self.server_url}{path}"

    async def _handle_response(self, response: httpx.Response, operation: str) -> Dict[str, Any]:
        """Handle API response and raise errors if needed."""
        if response.status_code >= 400:
            try:
                error_detail = response.json()
            except Exception:
                error_detail = response.text

            logger.error(f"{operation} failed: status={response.status_code}, detail={error_detail}")
            raise SandboxError(
                reason=f"{operation}失败",
                detail=f"HTTP {response.status_code}: {error_detail}"
            )

        if response.status_code == 204:
            return {}

        try:
            return response.json()
        except Exception:
            return {"content": response.text}

    # ==================== Session Management ====================

    async def create_session(
        self,
        cpu: str = "1",
        memory: str = "512Mi",
        disk: str = "1Gi",
        env_vars: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new sandbox session.

        Args:
            cpu: CPU cores allocation
            memory: Memory limit (e.g., "512Mi", "1Gi")
            disk: Disk limit (e.g., "1Gi", "10Gi")
            env_vars: Optional environment variables

        Returns:
            Session response with id, status, etc.
        """
        client = await self._get_client()

        payload = {
            "template_id": self.template_id,
            "timeout": self.timeout,
            "cpu": cpu,
            "memory": memory,
            "disk": disk
        }

        if self.session_id:
            payload["id"] = self.session_id

        if env_vars:
            payload["env_vars"] = env_vars

        logger.info(f"Creating session with payload: {payload}")

        response = await client.post("/api/v1/sessions", json=payload)
        result = await self._handle_response(response, "创建会话")

        self.session_id = result.get("id")
        self._session_created = True

        logger.info(f"Session created: {self.session_id}")
        return result

    async def get_session(self) -> Dict[str, Any]:
        """Get session details."""
        if not self.session_id:
            raise SandboxError(reason="获取会话失败", detail="session_id 未设置")

        client = await self._get_client()
        response = await client.get(f"/api/v1/sessions/{self.session_id}")
        return await self._handle_response(response, "获取会话")

    async def terminate_session(self) -> Dict[str, Any]:
        """Terminate the session (soft terminate, keeps records)."""
        if not self.session_id:
            raise SandboxError(reason="终止会话失败", detail="session_id 未设置")

        client = await self._get_client()
        response = await client.post(f"/api/v1/sessions/{self.session_id}/terminate")
        result = await self._handle_response(response, "终止会话")

        logger.info(f"Session terminated: {self.session_id}")
        return result

    async def delete_session(self) -> None:
        """Delete the session (hard delete, cascade deletes executions)."""
        if not self.session_id:
            raise SandboxError(reason="删除会话失败", detail="session_id 未设置")

        client = await self._get_client()
        response = await client.delete(f"/api/v1/sessions/{self.session_id}")
        await self._handle_response(response, "删除会话")

        logger.info(f"Session deleted: {self.session_id}")
        self.session_id = None
        self._session_created = False

    async def ensure_session(self) -> str:
        """
        Ensure session_id is available and optionally check if session exists.

        Note: This method does NOT create sessions proactively.
        The sandbox control plane API will create sessions automatically
        when needed (e.g., on first execute_code call).
        """
        if not self.session_id:
            raise SandboxError(reason="Session ID required", detail="session_id must be provided")

        # Already verified session exists
        if self._session_created:
            return self.session_id

        # Check if session exists
        try:
            session = await self.get_session()
            status = session.get("status", "")
            if status in ["running", "pending", "creating"]:
                self._session_created = True
                logger.debug(f"Session {self.session_id} exists with status: {status}")
            else:
                logger.debug(f"Session {self.session_id} status: {status}, will be created on first operation")
        except SandboxError:
            # Session doesn't exist yet, will be created on first operation
            logger.debug(f"Session {self.session_id} not found, will be created on first operation")

        return self.session_id

    # ==================== Code Execution ====================

    async def execute_code_sync(
        self,
        code: str,
        language: str = "python",
        timeout: int = DEFAULT_EXECUTION_TIMEOUT,
        event: Optional[Dict[str, Any]] = None,
        poll_interval: float = 0.5,
        sync_timeout: int = 300
    ) -> Dict[str, Any]:
        """
        Execute code synchronously (waits for result).

        Args:
            code: Code to execute
            language: Programming language (python, javascript, shell)
            timeout: Execution timeout in seconds
            event: Optional event data passed to handler
            poll_interval: Polling interval for sync execution
            sync_timeout: Maximum wait time for sync execution

        Returns:
            Execution result with stdout, stderr, return_value, etc.
        """
        await self.ensure_session()

        client = await self._get_client()

        payload = {
            "code": code,
            "language": language,
            "timeout": timeout
        }

        if event:
            payload["event"] = event

        params = {
            "poll_interval": poll_interval,
            "sync_timeout": sync_timeout
        }

        logger.info(f"Executing code (sync) in session {self.session_id}")

        response = await client.post(
            f"/api/v1/executions/sessions/{self.session_id}/execute-sync",
            json=payload,
            params=params
        )

        return await self._handle_response(response, "执行代码")

    async def execute_code_async(
        self,
        code: str,
        language: str = "python",
        timeout: int = DEFAULT_EXECUTION_TIMEOUT,
        event: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Submit code for asynchronous execution.

        Args:
            code: Code to execute
            language: Programming language (python, javascript, shell)
            timeout: Execution timeout in seconds
            event: Optional event data passed to handler

        Returns:
            Submission response with execution_id
        """
        await self.ensure_session()

        client = await self._get_client()

        payload = {
            "code": code,
            "language": language,
            "timeout": timeout
        }

        if event:
            payload["event"] = event

        logger.info(f"Submitting code (async) in session {self.session_id}")

        response = await client.post(
            f"/api/v1/executions/sessions/{self.session_id}/execute",
            json=payload
        )

        return await self._handle_response(response, "提交代码执行")

    async def get_execution_status(self, execution_id: str) -> Dict[str, Any]:
        """Get execution status."""
        client = await self._get_client()
        response = await client.get(f"/api/v1/executions/{execution_id}/status")
        return await self._handle_response(response, "获取执行状态")

    async def get_execution_result(self, execution_id: str) -> Dict[str, Any]:
        """Get execution result."""
        client = await self._get_client()
        response = await client.get(f"/api/v1/executions/{execution_id}/result")
        return await self._handle_response(response, "获取执行结果")

    async def wait_for_execution(
        self,
        execution_id: str,
        poll_interval: float = 0.5,
        max_wait: int = 300
    ) -> Dict[str, Any]:
        """
        Wait for async execution to complete.

        Args:
            execution_id: Execution ID to wait for
            poll_interval: Polling interval in seconds
            max_wait: Maximum wait time in seconds

        Returns:
            Final execution result
        """
        terminal_states = {"COMPLETED", "FAILED", "TIMEOUT", "CRASHED"}
        elapsed = 0

        while elapsed < max_wait:
            result = await self.get_execution_result(execution_id)
            status = result.get("status", "").upper()

            if status in terminal_states:
                return result

            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

        raise SandboxError(
            reason="执行超时",
            detail=f"等待执行结果超过 {max_wait} 秒"
        )

    # ==================== File Operations ====================

    async def list_files(
        self,
        path: Optional[str] = None,
        limit: int = 1000
    ) -> Dict[str, Any]:
        """
        List files in the session workspace.

        Args:
            path: Optional directory path to list
            limit: Maximum number of files to return

        Returns:
            List of files in the workspace
        """
        await self.ensure_session()

        client = await self._get_client()

        params = {"limit": limit}
        if path:
            params["path"] = path

        response = await client.get(
            f"/api/v1/sessions/{self.session_id}/files",
            params=params
        )

        return await self._handle_response(response, "列出文件")

    async def upload_file(
        self,
        file_path: str,
        content: bytes
    ) -> Dict[str, Any]:
        """
        Upload a file to the session workspace.

        Args:
            file_path: Path in the workspace where to save the file
            content: File content as bytes

        Returns:
            Upload response
        """
        await self.ensure_session()

        client = await self._get_client()

        files = {"file": (file_path, content)}

        response = await client.post(
            f"/api/v1/sessions/{self.session_id}/files/upload",
            params={"path": file_path},
            files=files
        )

        return await self._handle_response(response, "上传文件")

    async def download_file(self, file_path: str) -> bytes:
        """
        Download a file from the session workspace.

        Args:
            file_path: Path of the file in the workspace

        Returns:
            File content as bytes
        """
        await self.ensure_session()

        client = await self._get_client()

        response = await client.get(
            f"/api/v1/sessions/{self.session_id}/files/{file_path}"
        )

        if response.status_code >= 400:
            try:
                error_detail = response.json()
            except Exception:
                error_detail = response.text

            raise SandboxError(
                reason="下载文件失败",
                detail=f"HTTP {response.status_code}: {error_detail}"
            )

        return response.content
