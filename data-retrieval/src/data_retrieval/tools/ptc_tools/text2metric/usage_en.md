# PTC Text2Metric Usage

## Overview

The `Text2Metric` tool generates DIP metric query parameters from natural language and executes metric queries.

**Capabilities:**
- Convert natural language to metric queries
- Retrieve metric metadata
- Execute metric queries and return results
- Support knowledge network integration

---

## Usage

Call via `call_ptc_tool`, passing only `identity` and business parameters. The system automatically fetches `data_source`, `inner_llm`, `config` and other configuration parameters based on `identity`.

```python
from data_retrieval.tools.ptc_tools.registry import call_ptc_tool

# Query metrics
result = await call_ptc_tool("text2metric", {
    "identity": "user-123",
    "input": "Show CPU usage for the past hour",
    "action": "query"  # query=execute query, show_ds=view metadata
})

# View metadata
result = await call_ptc_tool("text2metric", {
    "identity": "user-123",
    "input": "",
    "action": "show_ds"
})
```

### Action Parameter

| action | Description |
|--------|-------------|
| `show_ds` | Get metric metadata |
| `query` | Execute metric query (default) |

---

## Parameters

### Business Parameters (passed at call time)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `identity` | str | Yes | Identifier for fetching configuration |
| `input` | str | Yes | Natural language query |
| `action` | str | No | Action type, defaults to `query` |
| `infos` | dict | No | Additional info (knowledge enhancement, etc.) |

### Configuration Parameters (auto-fetched from identity, no need to pass)

| Parameter | Description |
|-----------|-------------|
| `data_source.metric_list` | List of metric IDs |
| `data_source.base_url` | Server base URL |
| `data_source.token` | Authentication token |
| `data_source.user_id` | User ID |
| `inner_llm` | LLM configuration |
| `config.session_id` | Session ID |
| `config.force_limit` | Result limit |
| `config.recall_top_k` | Number of metrics to recall |

---

## Return Value

### query (Execute Query)

```json
{
  "output": {
    "title": "CPU Usage",
    "data": [...],
    "data_desc": {
      "return_records_num": 10,
      "real_records_num": 10
    },
    "metric_id": "metric_id_1",
    "query_params": {
      "start": 1646360670123,
      "end": 1646471470123,
      "step": "1m",
      "filters": []
    },
    "explanation": {...},
    "cites": [...]
  }
}
```

### show_ds (View Metadata)

```json
{
  "title": "Configured Metric Info",
  "message": "Currently configured with 2 metrics",
  "metric_num": 2,
  "metric_details": [...]
}
```

---

## Complete Example

```python
import asyncio
from data_retrieval.tools.ptc_tools.registry import call_ptc_tool

async def main():
    # 1. View metric metadata
    metadata = await call_ptc_tool("text2metric", {
        "identity": "demo-user",
        "input": "",
        "action": "show_ds"
    })
    print("Metadata:", metadata)
    
    # 2. Execute metric query
    result = await call_ptc_tool("text2metric", {
        "identity": "demo-user",
        "input": "Show CPU usage trend for the past hour",
        "action": "query"
    })
    print("Data:", result.get("output", {}).get("data"))

asyncio.run(main())
```

---

## Legacy Usage (Direct Instantiation)

Direct instantiation of PTC classes is still supported:

```python
from data_retrieval.tools.ptc_tools.text2metric import Text2Metric

tool = Text2Metric(agent_id="my-agent-id")  # Load config via agent_id
result = await tool.text2metric("Show CPU usage")
```

> **Note**: `call_ptc_tool` is recommended for consistency with MCP's parameter management.
