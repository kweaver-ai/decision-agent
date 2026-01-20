# -*- coding:utf-8 -*-
"""工具中断异常"""

from dataclasses import dataclass
from typing import Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from dolphin.core.coroutine.resume_handle import ResumeHandle


@dataclass
class ToolInterruptInfo:
    """工具中断信息
    
    对应接口文档 tool_interrupt_info.yaml
    
    Attributes:
        handle: 恢复句柄（ResumeHandle 对象）
        data: 中断详情（tool_name, tool_description, tool_args, interrupt_config）
    """
    handle: "ResumeHandle"  # 使用 Dolphin 的 ResumeHandle
    data: Dict[str, Any]    # 中断详情


class ToolInterruptException(Exception):
    """自定义工具中断异常
    
    用于在识别到 Dolphin SDK 的工具中断后，转换为自己的异常类进行处理。
    """
    
    def __init__(self, interrupt_info: ToolInterruptInfo):
        self.interrupt_info = interrupt_info
        tool_name = interrupt_info.data.get('tool_name', 'unknown') if interrupt_info.data else 'unknown'
        super().__init__(f"Tool interrupt: {tool_name}")
