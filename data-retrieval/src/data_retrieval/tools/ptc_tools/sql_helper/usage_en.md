# PTC SQL Helper Usage

## Overview

The `SQLHelper` tool provides direct SQL execution and data source metadata retrieval. Unlike `Text2SQL`, it executes pre-written SQL statements without natural language processing.

**Capabilities:**
- Execute SQL statements directly on data sources
- Retrieve data source metadata (structure, columns, dimensions, sample data)
- Maintain session context across queries
- Automatically add LIMIT clauses to prevent large result sets

**When to Use:**
- Use `SQLHelper` when you have SQL statements ready to execute
- Use `Text2SQL` when you want to query data using natural language

---

## Usage

Call via `call_ptc_tool`, passing only `identity` and business parameters. The system automatically fetches `data_source`, `config` and other configuration parameters based on `identity`.

```python
from data_retrieval.tools.ptc_tools.registry import call_ptc_tool

# Execute SQL
result = await call_ptc_tool("sql_helper", {
    "identity": "user-123",
    "command": "execute_sql",
    "sql": "SELECT * FROM orders LIMIT 10",
    "title": "Order Query"
})

# Get metadata
result = await call_ptc_tool("sql_helper", {
    "identity": "user-123",
    "command": "get_metadata",
    "title": "Sales Data"
})
```

### Command Parameter

| command | Description |
|---------|-------------|
| `get_metadata` | Get data source metadata |
| `execute_sql` | Execute SQL statement |

---

## Parameters

### Business Parameters (passed at call time)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `identity` | str | Yes | Identifier for fetching configuration |
| `command` | str | Yes | Command type: `get_metadata` or `execute_sql` |
| `sql` | str | Required for execute_sql | SQL statement |
| `title` | str | No | Data title |

### Configuration Parameters (auto-fetched from identity, no need to pass)

| Parameter | Description |
|-----------|-------------|
| `data_source.view_list` | List of view IDs |
| `data_source.user_id` | User ID |
| `data_source.base_url` | Server base URL |
| `data_source.token` | Authentication token |
| `config.session_id` | Session ID |
| `config.force_limit` | SQL LIMIT clause |
| `config.with_sample` | Include sample data |

---

## Return Value

### execute_sql

```json
{
  "output": {
    "command": "execute_sql",
    "sql": "SELECT * FROM orders LIMIT 10",
    "title": "Order Query",
    "data": [...],
    "data_desc": {
      "return_records_num": 10,
      "real_records_num": 10
    },
    "message": "SQL executed successfully"
  }
}
```

### get_metadata

```json
{
  "output": {
    "command": "get_metadata",
    "title": "Sales Data",
    "summary": [...],
    "metadata": [...],
    "sample": {...},
    "message": "Successfully retrieved metadata"
  }
}
```

---

## Complete Example

```python
import asyncio
from data_retrieval.tools.ptc_tools.registry import call_ptc_tool

async def main():
    # 1. Get metadata
    metadata = await call_ptc_tool("sql_helper", {
        "identity": "demo-user",
        "command": "get_metadata",
        "title": "Sales Data"
    })
    print("Metadata:", metadata)
    
    # 2. Execute SQL
    result = await call_ptc_tool("sql_helper", {
        "identity": "demo-user",
        "command": "execute_sql",
        "sql": "SELECT product_name, SUM(quantity) as total FROM orders GROUP BY product_name",
        "title": "Product Sales Summary"
    })
    print("Data:", result.get("output", {}).get("data"))

asyncio.run(main())
```

---

## Legacy Usage (Direct Instantiation)

Direct instantiation of PTC classes is still supported:

```python
from data_retrieval.tools.ptc_tools.sql_helper import SQLHelper

tool = SQLHelper(agent_id="my-agent-id")  # Load config via agent_id
result = await tool.execute_sql("SELECT * FROM orders LIMIT 10")
```

> **Note**: `call_ptc_tool` is recommended for consistency with MCP's parameter management.
