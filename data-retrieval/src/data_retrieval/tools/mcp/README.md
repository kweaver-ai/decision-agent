# MCP 服务说明文档

## 概述

本模块提供基于 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) 的工具服务，允许 AI 模型通过标准化协议调用 data-retrieval 中的各种工具。

### 核心特性

- **统一工具接口**：将所有 data-retrieval 工具暴露为 MCP 工具
- **Identity 参数管理**：通过 `identity` 标识符获取预设参数，避免 LLM 生成敏感配置
- **参数自动合并**：支持全局参数、工具参数、调用参数的多级合并
- **隐藏敏感参数**：从 `inputSchema` 中隐藏内部参数，LLM 不可见
- **双模式支持**：支持 stdio 和 SSE 两种通信模式
- **多服务分离**：支持按工具集启动独立的 MCP 服务

### MCP 能力支持

| 能力 | 说明 | 状态 |
|------|------|------|
| **Tools** | 工具调用 | ✅ 已实现 |
| **Prompts** | 提示模板 | ✅ 已实现 |
| **Resources** | 资源访问 | ✅ 已实现 |

---

## 两种工具服务

除了暴露全部工具的默认服务外，还提供两个独立的工具集服务：

| 服务 | 模块 | 默认端口 | 工具数 | 说明 |
|------|------|---------|--------|------|
| **全部工具** | `server_stdio` / `server_sse` | 9110 | 15 | 暴露所有工具 |
| **基础工具** | `server_base` | 9111 | 7 | text2sql, text2ngql, text2metric 等 |
| **沙箱工具** | `server_sandbox` | 9112 | 8 | execute_code, read_file 等 |

### 基础工具服务 (server_base)

包含数据查询相关的核心工具：

| 工具 | 说明 |
|------|------|
| `text2sql` | 自然语言转 SQL |
| `text2ngql` | 自然语言转 nGQL（图数据库） |
| `text2metric` | 自然语言转指标 |
| `sql_helper` | SQL 辅助工具 |
| `knowledge_item` | 知识条目查询 |
| `get_metadata` | 获取元数据 |
| `json2plot` | JSON 转图表 |

```bash
# stdio 模式
python -m data_retrieval.tools.mcp.server_base

# SSE 模式
python -m data_retrieval.tools.mcp.server_base --sse --port 9111
```

### 沙箱工具服务 (server_sandbox)

包含代码执行和文件操作相关工具：

| 工具 | 说明 |
|------|------|
| `execute_code` | 执行代码 |
| `execute_command` | 执行命令 |
| `read_file` | 读取文件 |
| `create_file` | 创建文件 |
| `list_files` | 列出文件 |
| `get_status` | 获取沙箱状态 |
| `close_sandbox` | 关闭沙箱 |
| `download_from_efast` | 从 Efast 下载 |

```bash
# stdio 模式
python -m data_retrieval.tools.mcp.server_sandbox

# SSE 模式
python -m data_retrieval.tools.mcp.server_sandbox --sse --port 9112
```

### SSE 多工具集模式（推荐）

启动一个 SSE 服务，通过不同 URL 路径连接不同工具集：

```bash
# 启动服务（默认多工具集模式）
python -m data_retrieval.tools.mcp.server_sse --port 9110
```

启动后可用端点：

| 工具集 | SSE 端点 | 工具列表端点 | 工具数 |
|--------|----------|-------------|--------|
| 全部 | `/sse` | `/tools` | 15 |
| 基础 | `/base/sse` | `/base/tools` | 7 |
| 沙箱 | `/sandbox/sse` | `/sandbox/tools` | 8 |

**Cursor 配置示例（SSE 模式）**：

```json
{
  "mcpServers": {
    "data-retrieval-base": {
      "url": "http://localhost:9110/base/sse?identity=12"
    },
    "data-retrieval-sandbox": {
      "url": "http://localhost:9110/sandbox/sse?identity=12"
    }
  }
}
```

> 💡 **注意**：`identity` 参数通过 URL 传递，服务器会在连接时解析并保存，后续工具调用自动使用该 identity 获取配置参数。

### stdio 模式（独立服务）

如果需要 stdio 模式，可以使用独立的服务器入口：

```json
{
  "mcpServers": {
    "data-retrieval-base": {
      "command": "python",
      "args": ["-m", "data_retrieval.tools.mcp.server_base"],
      "cwd": "D:/work/data-agent-opensource/data-retrieval/src"
    },
    "data-retrieval-sandbox": {
      "command": "python",
      "args": ["-m", "data_retrieval.tools.mcp.server_sandbox"],
      "cwd": "D:/work/data-agent-opensource/data-retrieval/src"
    },
    "data-retrieval-knowledge": {
      "command": "python",
      "args": ["-m", "data_retrieval.tools.mcp.server_knowledge"],
      "cwd": "D:/work/data-agent-opensource/data-retrieval/src"
    }
  }
}
```

---

## 两种服务模式

### stdio 模式 vs SSE 模式

| 特性 | stdio 模式 | SSE 模式 |
|------|-----------|----------|
| **通信方式** | stdin/stdout 管道 | HTTP/SSE 网络 |
| **启动方式** | 客户端自动 fork 子进程 | 需手动启动服务 |
| **后台运行** | ❌ 不支持 | ✅ 支持 |
| **多客户端** | ❌ 每次新进程 | ✅ 共享服务 |
| **适用场景** | IDE 集成 (Cursor/Claude) | 开发测试、服务部署 |
| **端口** | 不需要 | 需要（默认 9110） |

### stdio 模式工作原理

```
┌─────────────────────┐
│    客户端进程        │
│  (Python / Cursor)  │
└──────────┬──────────┘
           │ stdio_client() 
           │ 启动子进程 (fork/spawn)
           ▼
┌─────────────────────┐
│    子进程            │
│  (server_stdio.py)   │
└──────────┬──────────┘
           │
     stdin/stdout 管道
           │
     父子进程通过管道通信
```

**注意**：直接运行 `python server_stdio.py` 没有意义，因为它在等待 stdin 输入，但手动输入的不是 MCP 协议格式。

### SSE 模式工作原理

```
┌──────────────────┐     ┌──────────────────┐
│   客户端 A        │     │   客户端 B        │
└────────┬─────────┘     └────────┬─────────┘
         │                        │
         │ HTTP/SSE               │ HTTP/SSE
         └──────────┬─────────────┘
                    ▼
         ┌─────────────────────┐
         │   server_sse.py     │
         │   (长期运行服务)     │
         │   端口: 9110        │
         └─────────────────────┘
```

---

## 架构设计

```
┌─────────────────────────────────────────────────────────────────┐
│                        MCP Client                                │
│  (Cursor / Claude Desktop / Python Client)                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ stdio (管道) 或 SSE (HTTP)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              server_stdio.py / server_sse.py                     │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  build_server()                                              ││
│  │  ├── list_tools() → 列出所有公开工具                          ││
│  │  └── call_tool()  → 调用工具                                  ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       registry.py                                │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  call_mcp_tool(tool_name, arguments)                         ││
│  │  1. 提取 identity                                            ││
│  │  2. 从 Provider 获取参数                                      ││
│  │  3. 合并参数 (global → tool → llm)                           ││
│  │  4. 调用 tool.as_async_api_cls(params=merged)                ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ALL_TOOLS_MAPPING                             │
│  text2sql, text2ngql, text2metric, sql_helper, json2plot, ...   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 使用方法

### 方式一：stdio 模式（客户端自动启动服务器）

适用于 IDE 集成和测试脚本。

```bash
cd data-retrieval

# 测试脚本（自动启动 server_stdio.py 子进程）
python -m tests.mcp_test.client_example --list
python -m tests.mcp_test.client_example --full
python -m tests.mcp_test.client_example --call text2sql --input "查询数据"
```

Python 代码：

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    # 定义服务器启动参数
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "data_retrieval.tools.mcp.server_stdio"],
        cwd="path/to/data-retrieval/src",
    )
    
    # stdio_client 会自动 fork 子进程并通过管道通信
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # 设置参数
            await session.call_tool("_set_identity", {
                "identity": "user-123",
                "params": {"data_source": {...}, "inner_llm": {...}}
            })
            
            # 调用工具
            result = await session.call_tool("text2sql", {
                "identity": "user-123",
                "input": "查询数据",
                "action": "gen_exec"
            })
            print(result.content[0].text)
```

### 方式二：SSE 模式（先启动服务，再连接）

适用于开发测试和需要后台服务的场景。

```bash
# 第一步：启动 SSE 服务器（需设置环境变量配置 identity 对应的参数）
cd data-retrieval/src

# PowerShell
$env:DEFAULT_IDENTITY = "12"
$env:IDENTITY_PARAMS = '{"data_source": {...}, "inner_llm": {...}}'
python -m data_retrieval.tools.mcp.server_sse --port 9110

# 或后台启动（Linux/macOS）
export DEFAULT_IDENTITY=12
export IDENTITY_PARAMS='{"data_source": {...}}'
nohup python -m data_retrieval.tools.mcp.server_sse --port 9110 > mcp.log 2>&1 &
```

```bash
# 第二步：客户端连接（URL 中带 identity 参数）
cd data-retrieval

python -m tests.mcp_test.client_example --sse --list
python -m tests.mcp_test.client_example --sse --full
python -m tests.mcp_test.client_example --sse --identity user-123 --call text2sql --input "查询数据"

# 指定服务器地址
python -m tests.mcp_test.client_example --sse --sse-url http://192.168.1.100:9110/base/sse --list
```

验证服务状态：

```bash
curl http://localhost:9110/health   # 健康检查
curl http://localhost:9110/tools    # 查看工具列表
```

### 方式三：MCP Inspector（可视化调试）

```bash
cd data-retrieval/src
npx @anthropic/mcp-inspector python -m data_retrieval.tools.mcp.server_stdio
```

### 方式四：Cursor IDE 配置

在 `~/.cursor/mcp.json` 中添加：

```json
{
  "mcpServers": {
    "data-retrieval": {
      "command": "python",
      "args": ["-m", "data_retrieval.tools.mcp.server_stdio"],
      "cwd": "D:/work/data-agent-opensource/data-retrieval/src"
    }
  }
}
```

---

## 配置说明

### 环境变量

| 变量名 | 说明 | 格式 |
|--------|------|------|
| `DEFAULT_IDENTITY` | 默认 identity | 字符串 |
| `IDENTITY_PARAMS` | 完整参数（优先级最高） | JSON |
| `DATA_SOURCE` | 数据源配置 | JSON |
| `INNER_LLM` | LLM 配置 | JSON |
| `CONFIG` | 工具配置 | JSON |
| `SESSION_ID` | session_id（简单参数） | 字符串 |
| `TOKEN` | token（简单参数） | 字符串 |
| `TIMEOUT` | 超时时间（简单参数） | 数字 |
| `IDENTITY_PARAM_NAME` | identity 参数名（默认 "identity"） | 字符串 |

### 环境变量使用示例

```python
# 方式1：完整 JSON（推荐）
server_params = StdioServerParameters(
    command="python",
    args=["-m", "data_retrieval.tools.mcp.server_stdio"],
    cwd="path/to/src",
    env={
        "DEFAULT_IDENTITY": "user-123",
        "IDENTITY_PARAMS": json.dumps({
            "data_source": {"view_list": ["v1"], "user_id": "u1"},
            "inner_llm": {"id": "llm1", "name": "deepseek"},
            "config": {"session_id": "s1", "force_limit": 100}
        })
    }
)

# 方式2：分项 JSON
env={
    "DEFAULT_IDENTITY": "user-123",
    "DATA_SOURCE": '{"view_list": ["v1"], "user_id": "u1"}',
    "INNER_LLM": '{"id": "llm1", "name": "deepseek"}',
    "CONFIG": '{"session_id": "s1"}'
}

# 方式3：简单参数（兼容旧方式）
env={
    "DEFAULT_IDENTITY": "user-123",
    "SESSION_ID": "my-session",
    "TOKEN": "Bearer xxx"
}
```

使用环境变量后，调用工具时无需再调用 `_set_identity`：

```python
# 直接调用，参数已通过环境变量预设
result = await session.call_tool("text2sql", {
    "identity": "user-123",  # 与 DEFAULT_IDENTITY 匹配
    "input": "查询数据",
    "action": "gen_exec"
})
```

### 隐藏参数

以下参数会从 `inputSchema` 中隐藏（LLM 不可见）：

- `identity`
- `session_id`
- `token`
- `inner_llm`
- `inner_kg`
- `inner_datasource`
- `data_source`
- `config`

---

## 工作流程

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │     │   Server    │     │    Tool     │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       │  _set_identity    │                   │
       │  identity="123"   │                   │
       │  params={...}     │                   │
       │──────────────────>│                   │
       │   ok              │                   │
       │<──────────────────│                   │
       │                   │                   │
       │  text2sql         │                   │
       │  identity="123"   │                   │
       │  input="查询..."   │                   │
       │──────────────────>│                   │
       │                   │  从 Provider 获取  │
       │                   │  合并参数          │
       │                   │─────────┐         │
       │                   │<────────┘         │
       │                   │  as_async_api_cls │
       │                   │──────────────────>│
       │                   │                   │  执行
       │                   │    result         │
       │                   │<──────────────────│
       │   result          │                   │
       │<──────────────────│                   │
       │                   │                   │
```

---

## API 参考

### registry.py

```python
# 工具列表
list_mcp_tools() -> List[dict]

# 调用工具
await call_mcp_tool(tool_name: str, arguments: dict) -> Any
```

### prompts/

```python
# 获取所有提示模板
get_all_prompts() -> List[Dict]

# 获取指定提示
get_prompt(name: str) -> Dict | None

# 渲染消息
render_messages(prompt: Dict, args: Dict) -> List[Dict]
```

**内置提示**：`data_query`, `sql_generation`, `code_execution`

### resources/

```python
# 获取所有资源
get_all_resources() -> List[Dict]

# 获取所有资源模板
get_all_resource_templates() -> List[Dict]

# 读取资源
await read_resource(uri: str) -> Optional[str]
```

**内置资源**：`info://service`, `schema://{identity}`

---

## 文件结构

```
data_retrieval/tools/mcp/
├── __init__.py
├── registry.py          # 工具注册、参数管理、call_mcp_tool
├── server_common.py     # 服务器公共模块（配置、内部工具、结果转换）
├── session_store.py     # Session 存储抽象层（支持内存/Redis）
├── prompts/             # Prompts 模块
│   └── __init__.py      # 静态提示模板定义
├── resources/           # Resources 模块
│   └── __init__.py      # 静态资源定义
├── server_stdio.py      # stdio 模式 MCP 服务器（全部工具）
├── server_sse.py        # SSE 模式 MCP 服务器（全部工具）
├── server_base.py       # 基础工具服务器
├── server_sandbox.py    # 沙箱工具服务器
└── README.md            # 本文档
```

### 模块职责

| 模块 | 职责 |
|------|------|
| `registry.py` | 工具注册、参数管理、`call_mcp_tool` |
| `server_common.py` | 公共功能：环境配置、内部工具处理、服务器构建 |
| `session_store.py` | Session 存储：支持 InMemory 和 Redis 两种模式 |
| `prompts/` | 提示模板管理：注册、列表、渲染 |
| `resources/` | 资源管理：注册、列表、读取 |
| `server_stdio.py` | stdio 传输层：全部工具，通过管道通信 |
| `server_sse.py` | SSE 传输层：全部工具，通过 HTTP/SSE 通信 |
| `server_base.py` | 基础工具服务（text2sql 等 7 个工具） |
| `server_sandbox.py` | 沙箱工具服务（execute_code 等 8 个工具） |

---

## 常见问题

### Q: 直接运行 `python server_stdio.py` 有什么用？

**A**: 没有用。stdio 模式的服务器需要被 MCP 客户端启动，它通过 stdin/stdout 通信。直接运行会卡住等待输入。

### Q: 如何测试？

**A**: 
- 快速测试：`python -m tests.mcp_test.client_example --full`
- 后台服务测试：先启动 SSE 服务器，再用 `--sse` 连接

### Q: 两种模式如何选择？

**A**:
- **IDE 集成** (Cursor/Claude) → stdio 模式
- **开发调试**、**多客户端共享** → SSE 模式

---

## 参数传递方式

### stdio 模式
- **环境变量**：在启动服务器时设置 `DEFAULT_IDENTITY`、`IDENTITY_PARAMS` 等
- **_set_identity**：客户端调用内部工具动态设置参数

### SSE 模式
- **URL 参数**：在连接 URL 中带上 `?identity=xxx`（如 `/base/sse?identity=12`）
- **环境变量**：服务器启动时设置 `IDENTITY_PARAMS`，配置 identity 对应的参数

```
参数优先级：工具调用参数 > Session 参数 > 全局参数 > 环境变量参数
```

---

## 注意事项

1. **进程隔离**：stdio 模式下客户端和服务器是独立进程，客户端的 Python 变量不会影响服务器。

2. **Session 存储**（通过 `settings.MCP_SESSION_STORE` 配置）：
   - **默认**：`memory` - 内存存储，服务器重启后丢失
   - **生产环境**：`redis` - Redis 存储，支持多进程/分布式

3. **SSE 模式 Identity 传递**：
   - `identity` 通过 **URL 参数** 传递（如 `?identity=12`）
   - 服务器在 SSE 连接建立时解析 identity 并保存到 Session 存储
   - MCP session_id 与 identity 自动绑定，后续工具调用自动注入
   - 配置参数通过服务器端 **环境变量** 预先设置
   - SSE 连接断开时自动清理 Session

4. **Session 生命周期**（SSE 模式）：
   ```
   GET /sse?identity=12     → register_identity("12")
   POST /sse/messages?...   → bind_session(session_id) → identity
   工具调用                   → get_current_identity() → "12"
   SSE 断开                   → cleanup_session(session_id)
   ```