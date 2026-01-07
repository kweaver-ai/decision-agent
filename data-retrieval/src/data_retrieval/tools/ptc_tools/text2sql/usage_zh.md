# PTC Text2SQL 使用说明

## 概述

`Text2SQL` 工具将自然语言查询转换为 SQL 语句并在数据源上执行。它使用 LLM（大语言模型）理解用户意图，并基于数据源元数据生成准确的 SQL 查询。

**功能特性：**
- 将自然语言转换为 SQL，并提供解释和引用
- 检索数据源元数据（表、列、关系）
- 执行生成的 SQL 并返回查询结果
- 支持知识图谱/网络集成，增强上下文理解
- 自动添加 LIMIT 子句并处理查询重试

---

## 使用方法

通过 `call_ptc_tool` 调用，只需传入 `identity` 和业务参数。系统会根据 `identity` 自动获取 `data_source`、`inner_llm`、`config` 等配置参数。

```python
from data_retrieval.tools.ptc_tools.registry import call_ptc_tool

# 只需传入 identity 和业务参数
result = await call_ptc_tool("text2sql", {
    "identity": "user-123",
    "input": "按品牌显示销售额",
    "action": "gen_exec"  # gen_exec=生成并执行, gen=仅生成, show_ds=查看元数据
})
```

### action 参数说明

| action | 说明 |
|--------|------|
| `show_ds` | 获取数据源元数据 |
| `gen` | 仅生成 SQL（不执行） |
| `gen_exec` | 生成 SQL 并执行（最常用） |

---

## 参数说明

### 业务参数（调用时传入）

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `identity` | str | 是 | 用于获取配置的标识符 |
| `input` | str | 是 | 自然语言查询 |
| `action` | str | 否 | 动作类型，默认 `gen_exec` |
| `infos` | dict | 否 | 附加信息（知识增强等） |

### 配置参数（从 identity 自动获取，无需传入）

| 参数 | 说明 |
|------|------|
| `data_source.view_list` | 视图 ID 列表 |
| `data_source.user_id` | 用户 ID |
| `data_source.base_url` | 服务器基础 URL |
| `data_source.token` | 认证令牌 |
| `inner_llm` | LLM 配置 |
| `config.session_id` | 会话 ID |
| `config.force_limit` | SQL LIMIT 子句 |
| `config.retry_times` | 重试次数 |

---

## 返回值

### gen_exec（生成并执行）

```json
{
  "output": {
    "sql": "SELECT brand, SUM(sales) FROM orders GROUP BY brand LIMIT 100",
    "explanation": {...},
    "cites": [...],
    "data": [...],
    "title": "按品牌销售额",
    "data_desc": {
      "return_records_num": 10,
      "real_records_num": 10
    }
  }
}
```

### show_ds（查看元数据）

```json
{
  "output": {
    "data_summary": [...],
    "data_sources": {...},
    "title": "获取数据源信息"
  }
}
```

---

## 完整示例

```python
import asyncio
from data_retrieval.tools.ptc_tools.registry import call_ptc_tool

async def main():
    # 1. 查看数据源元数据
    metadata = await call_ptc_tool("text2sql", {
        "identity": "demo-user",
        "input": "",
        "action": "show_ds"
    })
    print("元数据:", metadata)
    
    # 2. 生成并执行 SQL
    result = await call_ptc_tool("text2sql", {
        "identity": "demo-user",
        "input": "查询销售额最高的前10个产品",
        "action": "gen_exec"
    })
    print("SQL:", result.get("output", {}).get("sql"))
    print("数据:", result.get("output", {}).get("data"))

asyncio.run(main())
```

---

## 传统用法（直接实例化）

仍然支持直接实例化 PTC 类的方式：

```python
from data_retrieval.tools.ptc_tools.text2sql import Text2SQL

tool = Text2SQL(agent_id="my-agent-id")  # 通过 agent_id 加载配置
result = await tool.text2sql("按品牌显示销售额")
```

> **注意**：推荐使用 `call_ptc_tool` 方式，与 MCP 保持一致的参数管理机制。
