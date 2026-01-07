# PTC Text2Metric 使用说明

## 概述

`Text2Metric` 工具从自然语言生成 DIP 指标调用参数并执行指标查询。

**功能特性：**
- 将自然语言转换为指标查询
- 检索指标元数据
- 执行指标查询并返回结果
- 支持知识网络集成

---

## 使用方法

通过 `call_ptc_tool` 调用，只需传入 `identity` 和业务参数。系统会根据 `identity` 自动获取 `data_source`、`inner_llm`、`config` 等配置参数。

```python
from data_retrieval.tools.ptc_tools.registry import call_ptc_tool

# 查询指标
result = await call_ptc_tool("text2metric", {
    "identity": "user-123",
    "input": "显示过去一小时的 CPU 使用率",
    "action": "query"  # query=执行查询, show_ds=查看元数据
})

# 查看元数据
result = await call_ptc_tool("text2metric", {
    "identity": "user-123",
    "input": "",
    "action": "show_ds"
})
```

### action 参数说明

| action | 说明 |
|--------|------|
| `show_ds` | 获取指标元数据 |
| `query` | 执行指标查询（默认） |

---

## 参数说明

### 业务参数（调用时传入）

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `identity` | str | 是 | 用于获取配置的标识符 |
| `input` | str | 是 | 自然语言查询 |
| `action` | str | 否 | 动作类型，默认 `query` |
| `infos` | dict | 否 | 附加信息（知识增强等） |

### 配置参数（从 identity 自动获取，无需传入）

| 参数 | 说明 |
|------|------|
| `data_source.metric_list` | 指标 ID 列表 |
| `data_source.base_url` | 服务器基础 URL |
| `data_source.token` | 认证令牌 |
| `data_source.user_id` | 用户 ID |
| `inner_llm` | LLM 配置 |
| `config.session_id` | 会话 ID |
| `config.force_limit` | 结果限制 |
| `config.recall_top_k` | 召回指标数量 |

---

## 返回值

### query（执行查询）

```json
{
  "output": {
    "title": "CPU 使用率",
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

### show_ds（查看元数据）

```json
{
  "title": "配置的指标信息",
  "message": "当前配置了 2 个指标",
  "metric_num": 2,
  "metric_details": [...]
}
```

---

## 完整示例

```python
import asyncio
from data_retrieval.tools.ptc_tools.registry import call_ptc_tool

async def main():
    # 1. 查看指标元数据
    metadata = await call_ptc_tool("text2metric", {
        "identity": "demo-user",
        "input": "",
        "action": "show_ds"
    })
    print("元数据:", metadata)

    # 2. 执行指标查询
    result = await call_ptc_tool("text2metric", {
        "identity": "demo-user",
        "input": "显示过去一小时的 CPU 使用率趋势",
        "action": "query"
    })
    print("数据:", result.get("output", {}).get("data"))

asyncio.run(main())
```

---

## 传统用法（直接实例化）

仍然支持直接实例化 PTC 类的方式：

```python
from data_retrieval.tools.ptc_tools.text2metric import Text2Metric

tool = Text2Metric(agent_id="my-agent-id")  # 通过 agent_id 加载配置
result = await tool.text2metric("显示 CPU 使用率")
```

> **注意**：推荐使用 `call_ptc_tool` 方式，与 MCP 保持一致的参数管理机制。
