# -*- coding:utf-8 -*-
"""
请求信息格式化
"""

import json
from typing import Dict, Any

from ..constants import COLORS, RESET, BOLD
from .table_drawer import TableDrawer


def format_request_info(
    request_info: Dict[str, Any], colorize: bool = False, indent: int = 2
) -> str:
    """
    格式化请求信息为表格形式

    Args:
        request_info: 请求信息字典
        colorize: 是否添加颜色
        indent: 缩进空格数

    Returns:
        str: 格式化后的请求信息
    """
    indent_str = " " * indent
    lines = []

    # 标题
    if colorize:
        lines.append(f"{indent_str}{BOLD}📋 REQUEST DETAILS{RESET}")
    else:
        lines.append(f"{indent_str}📋 REQUEST DETAILS")

    # 基本信息（使用列表形式，不截断 URL）
    if "method" in request_info:
        if colorize:
            lines.append(
                f"{indent_str}  {COLORS['key']}🔹 Method:{RESET} {COLORS['value']}{request_info['method']}{RESET}"
            )
        else:
            lines.append(f"{indent_str}  🔹 Method: {request_info['method']}")

    if "url" in request_info:
        # URL 不截断，完整显示
        if colorize:
            lines.append(f"{indent_str}  {COLORS['key']}🔹 URL:{RESET}")
            lines.append(
                f"{indent_str}    {COLORS['value']}{request_info['url']}{RESET}"
            )
        else:
            lines.append(f"{indent_str}  🔹 URL:")
            lines.append(f"{indent_str}    {request_info['url']}")
    elif "path" in request_info:
        if colorize:
            lines.append(
                f"{indent_str}  {COLORS['key']}🔹 Path:{RESET} {COLORS['value']}{request_info['path']}{RESET}"
            )
        else:
            lines.append(f"{indent_str}  🔹 Path: {request_info['path']}")

    if "query_string" in request_info and request_info["query_string"]:
        if colorize:
            lines.append(
                f"{indent_str}  {COLORS['key']}🔹 Query:{RESET} {COLORS['value']}{request_info['query_string']}{RESET}"
            )
        else:
            lines.append(f"{indent_str}  🔹 Query: {request_info['query_string']}")

    if "client_ip" in request_info:
        if colorize:
            lines.append(
                f"{indent_str}  {COLORS['key']}🔹 Client IP:{RESET} {COLORS['value']}{request_info['client_ip']}{RESET}"
            )
        else:
            lines.append(f"{indent_str}  🔹 Client IP: {request_info['client_ip']}")

    if "account_id" in request_info:
        if colorize:
            lines.append(
                f"{indent_str}  {COLORS['key']}🔹 Account ID:{RESET} {COLORS['value']}{request_info['account_id']}{RESET}"
            )
        else:
            lines.append(f"{indent_str}  🔹 Account ID: {request_info['account_id']}")

    if "account_type" in request_info:
        if colorize:
            lines.append(
                f"{indent_str}  {COLORS['key']}🔹 Account Type:{RESET} {COLORS['value']}{request_info['account_type']}{RESET}"
            )
        else:
            lines.append(
                f"{indent_str}  🔹 Account Type: {request_info['account_type']}"
            )

    if "biz_domain" in request_info:
        if colorize:
            lines.append(
                f"{indent_str}  {COLORS['key']}🔹 Biz Domain:{RESET} {COLORS['value']}{request_info['biz_domain']}{RESET}"
            )
        else:
            lines.append(f"{indent_str}  🔹 Biz Domain: {request_info['biz_domain']}")

    lines.append("")  # 空行分隔

    # Headers 表格
    if "headers" in request_info and request_info["headers"]:
        lines.append("")
        if colorize:
            lines.append(f"{indent_str}  {COLORS['key']}📨 Headers:{RESET}")
        else:
            lines.append(f"{indent_str}  📨 Headers:")

        header_rows = []
        # 过滤敏感和不重要的 headers
        skip_headers = {
            "host",
            "connection",
            "accept",
            "accept-encoding",
            "accept-language",
        }
        for key, value in request_info["headers"].items():
            if key.lower() not in skip_headers:
                # 截断过长的值
                display_value = str(value)
                if len(display_value) > 60:
                    display_value = display_value[:57] + "..."
                header_rows.append([key, display_value])

        if header_rows:
            lines.append(
                TableDrawer.draw_table(
                    headers=["Header", "Value"],
                    rows=header_rows,
                    col_widths=[25, 60],
                    colorize=colorize,
                    indent=indent + 4,
                )
            )

    # Body
    if "body" in request_info and request_info["body"]:
        lines.append("")
        if colorize:
            lines.append(f"{indent_str}  {COLORS['key']}📦 Request Body:{RESET}")
        else:
            lines.append(f"{indent_str}  📦 Request Body:")

        body = request_info["body"]
        if isinstance(body, dict):
            try:
                body_str = json.dumps(body, ensure_ascii=False, indent=4)
            except:
                body_str = str(body)
        else:
            body_str = str(body)

        # 截断过长的 body
        if len(body_str) > 500:
            body_str = body_str[:500] + "\n... (truncated)"

        for line in body_str.split("\n"):
            if colorize:
                lines.append(f"{indent_str}    {COLORS['value']}{line}{RESET}")
            else:
                lines.append(f"{indent_str}    {line}")

    return "\n".join(lines)
