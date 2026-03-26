from typing import Any, Dict
import json

from app.common.stand_log import StandLogger

# Import from common module using relative import
from ..common import ToolMapInfo


def process_fixed_value(
    tool_map_item: ToolMapInfo,
    current_tool_input: Dict[str, Any],
    input_params: Dict[str, Any],
):
    """处理 fixedValue 类型的映射值"""

    val = tool_map_item.get_map_value()
    input_type = tool_map_item.input_type

    # Use a local variable to avoid mutating tool_map_item.map_value.
    # Mutating the shared ToolMapInfo object would cause spurious warnings on
    # repeated invocations (second call would try json.loads on an already-parsed
    # dict, fail, and log "不是json格式" unnecessarily).
    parsed_val = val
    if isinstance(val, str):
        if input_type != "string":
            try:
                parsed_val = json.loads(val)
            except Exception:
                StandLogger.warn(
                    f"工具的输入参数{tool_map_item.input_name}的值{val}不是json格式"
                )
                parsed_val = val
        else:
            if val.startswith('"') and val.endswith('"'):
                parsed_val = json.loads(val)

    current_tool_input[tool_map_item.input_name] = parsed_val
