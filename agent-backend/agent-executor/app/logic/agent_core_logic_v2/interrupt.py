import json
from typing import Any, Dict, Optional
from dolphin.core.utils.tools import ToolInterrupt

from app.common.stand_log import StandLogger
from app.utils.json import custom_serializer
from app.utils.observability.trace_wrapper import internal_span
from opentelemetry.trace import Span

from .trace import span_set_attrs


class InterruptHandler:
    @classmethod
    @internal_span()
    async def handle_tool_interrupt(
        cls,
        tool_interrupt: ToolInterrupt,
        res: Dict[str, Any],
        context_variables: Dict[str, Any],
        span: Optional[Span] = None,
    ) -> None:
        """处理工具中断

        Args:
            tool_interrupt: 工具中断异常
            res: 结果字典
            context_variables: 上下文变量
            event_key: 事件键（agent_run_id）
        """

        span_set_attrs(
            span=span,
            agent_run_id=context_variables.get("session_id", ""),
            agent_id=context_variables.get("agent_id", ""),
        )

        StandLogger.info(f"ToolInterrupt: {tool_interrupt}")

        # 直接使用整体 handle（从 ToolInterrupt 获取）
        handle = getattr(tool_interrupt, 'handle', None)
        
        # 构建中断数据
        interrupt_data = {
            "tool_name": tool_interrupt.tool_name,
            "tool_args": tool_interrupt.tool_args,
        }

        # 设置 interrupt_info（替代原来的 ask）
        res["interrupt_info"] = {
            "handle": handle,
            "data": interrupt_data,
        }

        res["status"] = "True"

        StandLogger.info(
            f"ToolInterrupt res: {json.dumps(res, ensure_ascii=False, default=custom_serializer)}"
        )
