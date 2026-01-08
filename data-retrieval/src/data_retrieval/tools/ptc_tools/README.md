# PTC (Programmatic Tool Composition) 工具说明

## 概述

PTC 是一种编程方式调用工具的范式，提供与 MCP 一致的 identity-based 参数管理机制。

### 核心特性

- **Identity 参数管理**：通过 `identity` 标识符从 Provider 获取配置参数
- **与 MCP 共享 Provider**：复用 `IdentityParamsProvider`，MCP 和 PTC 共享同一套参数
- **直接调用 base_tools**：底层调用 `Text2SQLTool.as_async_api_cls()` 等

---

## 架构

```
┌─────────────────────────────────────────────────────────────────┐
│                      调用方                                      │
│  (Python 脚本 / API / Agent)                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ call_ptc_tool(tool_name, arguments)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ptc_tools/registry.py                          │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  1. 验证工具存在                                             ││
│  │  2. 提取 identity                                            ││
│  │  3. 从 Provider 获取参数                                     ││
│  │  4. 合并参数: global → tool → call                           ││
│  │  5. 调用 base_tool.as_async_api_cls(params=merged)           ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   base_tools (Text2SQLTool, etc.)                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 使用方法

### 通过 `call_ptc_tool` 调用（推荐）

系统会根据 `identity` 自动从 Provider 获取配置参数，调用方只需传入业务参数：

```python
import asyncio
from data_retrieval.tools.ptc_tools.registry import call_ptc_tool

async def main():
    # 调用工具（只传业务参数，其他参数自动从 identity 获取）
    result = await call_ptc_tool("text2sql", {
        "identity": "user-123",
        "input": "查询销售额最高的产品",
        "action": "gen_exec"
    })
    
    print(result)

asyncio.run(main())
```

### 直接实例化 PTC 类（传统方式）

```python
from data_retrieval.tools.ptc_tools.text2sql import Text2SQL

async def main():
    # 通过 agent_id 加载配置（从远程服务器或本地文件）
    tool = Text2SQL(agent_id="my-agent-id")
    
    # 调用方法
    result = await tool.text2sql(
        input="查询销售额最高的产品",
        # data_source 和 config 从配置自动加载
    )
    print(result)
```

---

## 参数管理

### 参数合并优先级

```
调用参数 > 工具参数 > 全局参数
```

### 配置参数（从 identity 自动获取）

以下参数由系统根据 `identity` 自动获取，不需要调用方传入：

- `data_source`：数据源配置
- `inner_llm`：LLM 配置
- `config`：工具配置
- `token`：认证令牌
- `session_id`：会话 ID

---

## 可用工具

| 工具名 | 说明 | 对应 base_tool |
|--------|------|----------------|
| `text2sql` | 自然语言转 SQL | `Text2SQLTool` |
| `text2metric` | 自然语言查询指标 | `Text2DIPMetricTool` |
| `sql_helper` | SQL 执行助手 | `SQLHelperTool` |

---

## API 参考

### registry.py

```python
# 调用 PTC 工具
await call_ptc_tool(tool_name: str, arguments: dict) -> Any

# 获取工具映射
get_ptc_tools_mapping() -> Dict[str, Type]

# 获取合并后的参数
get_ptc_tool_params(tool_name: str, arguments: dict) -> dict
```

---

## 与 MCP 的关系

| 特性 | MCP | PTC |
|------|-----|-----|
| 调用方式 | `call_mcp_tool()` | `call_ptc_tool()` |
| Provider | `IdentityParamsProvider` | 复用 MCP 的 Provider |
| 参数来源 | identity + LLM 参数 | identity + 调用参数 |
| 底层实现 | `tool.as_async_api_cls()` | 同 |
| 使用场景 | AI 模型调用 | 程序直接调用 |

---

## 文件结构

```
ptc_tools/
├── __init__.py
├── registry.py          # 工具注册、参数管理、call_ptc_tool
├── base.py             # PTCBaseTool 基类（传统方式）
├── tool_search.py      # 工具搜索
├── text2sql/           # Text2SQL 工具
├── text2metric/        # Text2Metric 工具
├── sql_helper/         # SQL Helper 工具
└── README.md           # 本文档
```
