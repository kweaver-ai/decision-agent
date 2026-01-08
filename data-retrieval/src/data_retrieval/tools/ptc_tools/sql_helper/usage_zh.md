# PTC SQL Helper 使用说明

## 概述

`SQLHelper` 工具提供直接的 SQL 执行和数据源元数据检索功能。与 `Text2SQL` 不同，它执行已提供的 SQL 语句（不进行自然语言处理）。

**功能特性：**
- 直接在数据源上执行 SQL 语句
- 检索数据源元数据（结构、列、维度、样本数据）
- 在多个查询之间维护会话上下文
- 自动添加 LIMIT 子句以防止返回大量结果集

**何时使用：**
- 当您已有 SQL 语句需要执行时，使用 `SQLHelper`
- 当您想使用自然语言查询数据时，使用 `Text2SQL`

---

## 使用方法

通过 `call_ptc_tool` 调用，只需传入 `identity` 和业务参数。系统会根据 `identity` 自动获取 `data_source`、`config` 等配置参数。

```python
from data_retrieval.tools.ptc_tools.registry import call_ptc_tool

# 执行 SQL
result = await call_ptc_tool("sql_helper", {
    "identity": "user-123",
    "command": "execute_sql",
    "sql": "SELECT * FROM orders LIMIT 10",
    "title": "订单查询"
})

# 获取元数据
result = await call_ptc_tool("sql_helper", {
    "identity": "user-123",
    "command": "get_metadata",
    "title": "销售数据"
})
```

### command 参数说明

| command | 说明 |
|---------|------|
| `get_metadata` | 获取数据源元数据 |
| `execute_sql` | 执行 SQL 语句 |

---

## 参数说明

### 业务参数（调用时传入）

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `identity` | str | 是 | 用于获取配置的标识符 |
| `command` | str | 是 | 命令类型：`get_metadata` 或 `execute_sql` |
| `sql` | str | execute_sql 时必需 | SQL 语句 |
| `title` | str | 否 | 数据标题 |

### 配置参数（从 identity 自动获取，无需传入）

| 参数 | 说明 |
|------|------|
| `data_source.view_list` | 视图 ID 列表 |
| `data_source.user_id` | 用户 ID |
| `data_source.base_url` | 服务器基础 URL |
| `data_source.token` | 认证令牌 |
| `config.session_id` | 会话 ID |
| `config.force_limit` | SQL LIMIT 子句 |
| `config.with_sample` | 是否包含样本数据 |

---

## 返回值

### execute_sql

```json
{
  "output": {
    "command": "execute_sql",
    "sql": "SELECT * FROM orders LIMIT 10",
    "title": "订单查询",
    "data": [...],
    "data_desc": {
      "return_records_num": 10,
      "real_records_num": 10
    },
    "message": "SQL 执行成功"
  }
}
```

### get_metadata

```json
{
  "output": {
    "command": "get_metadata",
    "title": "销售数据",
    "summary": [...],
    "metadata": [...],
    "sample": {...},
    "message": "成功检索元数据"
  }
}
```

---

## 完整示例

```python
import asyncio
from data_retrieval.tools.ptc_tools.registry import call_ptc_tool

async def main():
    # 1. 获取元数据
    metadata = await call_ptc_tool("sql_helper", {
        "identity": "demo-user",
        "command": "get_metadata",
        "title": "销售数据"
    })
    print("元数据:", metadata)
    
    # 2. 执行 SQL
    result = await call_ptc_tool("sql_helper", {
        "identity": "demo-user",
        "command": "execute_sql",
        "sql": "SELECT product_name, SUM(quantity) as total FROM orders GROUP BY product_name",
        "title": "产品销量统计"
    })
    print("数据:", result.get("output", {}).get("data"))

asyncio.run(main())
```

---

## 传统用法（直接实例化）

仍然支持直接实例化 PTC 类的方式：

```python
from data_retrieval.tools.ptc_tools.sql_helper import SQLHelper

tool = SQLHelper(agent_id="my-agent-id")  # 通过 agent_id 加载配置
result = await tool.execute_sql("SELECT * FROM orders LIMIT 10")
```

> **注意**：推荐使用 `call_ptc_tool` 方式，与 MCP 保持一致的参数管理机制。
