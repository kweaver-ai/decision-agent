# -*- coding: utf-8 -*-
"""
MCP Prompts 模块 - 静态提示模板
"""

from typing import List, Dict, Any

# 提示模板定义
PROMPTS = [
    {
        "name": "data_query",
        "description": "数据查询助手提示，引导用户进行自然语言数据查询",
        "arguments": [
            {"name": "table_info", "description": "可用表信息", "required": False},
        ],
        "messages": [
            {
                "role": "system",
                "content": """你是一个数据查询助手，帮助用户用自然语言查询数据。

可用的查询工具：
- text2sql: 将自然语言转换为 SQL 查询
- text2ngql: 将自然语言转换为图数据库查询（nGQL）
- text2metric: 查询指标数据

{table_info}

请根据用户的问题选择合适的工具进行查询。"""
            },
        ],
    },
    {
        "name": "sql_generation",
        "description": "SQL 生成提示",
        "arguments": [
            {"name": "schema", "description": "数据库 schema 信息", "required": True},
            {"name": "question", "description": "用户问题", "required": True},
        ],
        "messages": [
            {
                "role": "system",
                "content": """你是一个 SQL 专家。根据以下数据库 schema 生成 SQL 查询。

Schema:
{schema}

注意事项：
1. 只生成 SELECT 查询
2. 使用标准 SQL 语法
3. 添加适当的 LIMIT"""
            },
            {
                "role": "user",
                "content": "{question}"
            },
        ],
    },
    {
        "name": "code_execution",
        "description": "代码执行助手提示",
        "arguments": [
            {"name": "language", "description": "编程语言", "required": False},
        ],
        "messages": [
            {
                "role": "system",
                "content": """你是一个代码执行助手，可以在沙箱环境中执行代码。

支持的操作：execute_code, execute_command, read_file, create_file, list_files

编程语言: {language}"""
            },
        ],
    },
]


def get_all_prompts() -> List[Dict[str, Any]]:
    """获取所有提示模板。"""
    return PROMPTS


def get_prompt(name: str) -> Dict[str, Any] | None:
    """获取指定提示模板。"""
    for p in PROMPTS:
        if p["name"] == name:
            return p
    return None


def render_messages(prompt: Dict[str, Any], args: Dict[str, Any]) -> List[Dict[str, str]]:
    """渲染提示消息。"""
    messages = []
    for msg in prompt.get("messages", []):
        content = msg["content"]
        for key, value in args.items():
            content = content.replace(f"{{{key}}}", str(value) if value else "")
        messages.append({"role": msg["role"], "content": content})
    return messages
