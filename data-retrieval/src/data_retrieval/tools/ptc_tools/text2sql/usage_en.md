# PTC Text2SQL Usage

## Overview

The `Text2SQL` tool converts natural language queries into SQL statements and executes them against data sources. It uses LLM to understand user intent and generate accurate SQL queries based on data source metadata.

**Capabilities:**
- Converts natural language to SQL with explanations and citations
- Retrieves data source metadata (tables, columns, relationships)
- Executes generated SQL and returns query results
- Supports knowledge graph/network integration for enhanced context
- Automatically adds LIMIT clauses and handles query retries

---

## Usage

Call via `call_ptc_tool`, passing only `identity` and business parameters. The system automatically fetches `data_source`, `inner_llm`, `config` and other configuration parameters based on `identity`.

```python
from data_retrieval.tools.ptc_tools.registry import call_ptc_tool

# Only pass identity and business parameters
result = await call_ptc_tool("text2sql", {
    "identity": "user-123",
    "input": "Show sales by brand",
    "action": "gen_exec"  # gen_exec=generate and execute, gen=generate only, show_ds=view metadata
})
```

### Action Parameter

| action | Description |
|--------|-------------|
| `show_ds` | Get data source metadata |
| `gen` | Generate SQL only (no execution) |
| `gen_exec` | Generate SQL and execute (most common) |

---

## Parameters

### Business Parameters (passed at call time)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `identity` | str | Yes | Identifier for fetching configuration |
| `input` | str | Yes | Natural language query |
| `action` | str | No | Action type, defaults to `gen_exec` |
| `infos` | dict | No | Additional info (knowledge enhancement, etc.) |

### Configuration Parameters (auto-fetched from identity, no need to pass)

| Parameter | Description |
|-----------|-------------|
| `data_source.view_list` | List of view IDs |
| `data_source.user_id` | User ID |
| `data_source.base_url` | Server base URL |
| `data_source.token` | Authentication token |
| `inner_llm` | LLM configuration |
| `config.session_id` | Session ID |
| `config.force_limit` | SQL LIMIT clause |
| `config.retry_times` | Number of retries |

---

## Return Value

### gen_exec (Generate and Execute)

```json
{
  "output": {
    "sql": "SELECT brand, SUM(sales) FROM orders GROUP BY brand LIMIT 100",
    "explanation": {...},
    "cites": [...],
    "data": [...],
    "title": "Sales by Brand",
    "data_desc": {
      "return_records_num": 10,
      "real_records_num": 10
    }
  }
}
```

### show_ds (View Metadata)

```json
{
  "output": {
    "data_summary": [...],
    "data_sources": {...},
    "title": "Get Data Source Info"
  }
}
```

---

## Complete Example

```python
import asyncio
from data_retrieval.tools.ptc_tools.registry import call_ptc_tool

async def main():
    # 1. View data source metadata
    metadata = await call_ptc_tool("text2sql", {
        "identity": "demo-user",
        "input": "",
        "action": "show_ds"
    })
    print("Metadata:", metadata)
    
    # 2. Generate and execute SQL
    result = await call_ptc_tool("text2sql", {
        "identity": "demo-user",
        "input": "Show top 10 products by sales",
        "action": "gen_exec"
    })
    print("SQL:", result.get("output", {}).get("sql"))
    print("Data:", result.get("output", {}).get("data"))

asyncio.run(main())
```

---

## Legacy Usage (Direct Instantiation)

Direct instantiation of PTC classes is still supported:

```python
from data_retrieval.tools.ptc_tools.text2sql import Text2SQL

tool = Text2SQL(agent_id="my-agent-id")  # Load config via agent_id
result = await tool.text2sql("Show sales by brand")
```

> **Note**: `call_ptc_tool` is recommended for consistency with MCP's parameter management.
