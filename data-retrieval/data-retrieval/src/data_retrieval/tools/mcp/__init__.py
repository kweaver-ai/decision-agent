# -*- coding: utf-8 -*-
"""
MCP integration (Model Context Protocol).

This package provides:
- A tool registry adapter that can expose existing tools as MCP tool specs
- A unified call path to invoke tools in-process (no FastAPI forwarding)

Transport/server implementation is intentionally kept separate so you can plug in
any MCP Python SDK (stdio, http, etc.) without changing tool logic.
"""


