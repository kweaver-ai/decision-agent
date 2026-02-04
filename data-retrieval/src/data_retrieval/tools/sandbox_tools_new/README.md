# 新沙箱工具包 (Sandbox Toolkit New)

这个目录包含使用 RESTful API 实现的新版沙箱工具。相比旧版工具，新版工具具有以下优势：

- 使用 RESTful API 直接调用沙箱控制面
- 支持同步/异步执行模式
- 更好的会话管理（自动创建会话）
- 默认使用 `python-basic` 模板
- 使用 `user_id` 自动生成 `session_id`（格式：`sess-{user_id}`）

## 工具列表

### 1. ExecuteCodeTool - 执行代码工具
- **API 路径**: `/tools/execute_code`
- **功能**: 在沙箱环境中执行代码
- **支持**: Python、JavaScript、Shell
- **参数**:
  - `code`: 要执行的代码内容（需定义 `handler(event)` 函数）
  - `language`: 编程语言（python/javascript/shell，默认 python）
  - `event`: 传递给 handler 函数的事件参数（可选）
  - `timeout`: 执行超时时间，秒（默认 30）
  - `sync_execution`: 是否使用同步执行模式（默认 true）
  - `template_id`: 沙箱模板ID（默认 python-basic）
  - `user_id`: 用户ID，用于生成会话ID（格式：sess-{user_id}），不提供则自动生成
  - `title`: 操作描述（可选）

### 2. CreateFileTool - 创建文件工具
- **API 路径**: `/tools/create_file`
- **功能**: 在沙箱环境中创建/上传文件
- **参数**:
  - `filename`: 要创建的文件名（必填）
  - `content`: 文件内容（可选，与 result_cache_key 二选一）
  - `result_cache_key`: 从缓存获取内容的 key（可选）
  - `template_id`: 沙箱模板ID（默认 python-basic）
  - `user_id`: 用户ID，用于生成会话ID（格式：sess-{user_id}），不提供则自动生成
  - `title`: 操作描述（可选）

### 3. ReadFileTool - 读取文件工具
- **API 路径**: `/tools/read_file`
- **功能**: 读取/下载沙箱环境中的文件
- **参数**:
  - `filename`: 要读取的文件名（必填）
  - `result_cache_key`: 缓存结果的 key（可选）
  - `template_id`: 沙箱模板ID（默认 python-basic）
  - `user_id`: 用户ID，用于生成会话ID（格式：sess-{user_id}），不提供则自动生成
  - `title`: 操作描述（可选）

### 4. ListFilesTool - 列出文件工具
- **API 路径**: `/tools/list_files`
- **功能**: 列出沙箱环境中的文件
- **参数**:
  - `path`: 要列出的目录路径（默认 `/`）
  - `template_id`: 沙箱模板ID（默认 python-basic）
  - `user_id`: 用户ID，用于生成会话ID（格式：sess-{user_id}），不提供则自动生成
  - `title`: 操作描述（可选）

### 5. TerminateSessionTool - 终止会话工具
- **API 路径**: `/tools/terminate_session`
- **功能**: 终止沙箱会话（软终止）
- **参数**:
  - `user_id`: 要终止的用户ID（必填，用于生成 session_id）
  - `template_id`: 沙箱模板ID（默认 python-basic）
  - `title`: 操作描述（可选）

## 使用方法

### 基本使用

```python
from data_retrieval.tools.sandbox_tools_new import ExecuteCodeTool, CreateFileTool

# 创建工具实例（自动使用 python-basic 模板）
execute_tool = ExecuteCodeTool(user_id="my_user")

# 执行代码
result = await execute_tool.ainvoke({
    "code": """
def handler(event):
    return {"message": "Hello World", "result": 1 + 1}
""",
    "title": "执行 Hello World 示例"
})
```

### 创建和读取文件

```python
from data_retrieval.tools.sandbox_tools_new import CreateFileTool, ReadFileTool

user_id = "file_test"

# 创建文件
create_tool = CreateFileTool(user_id=user_id)
await create_tool.ainvoke({
    "filename": "test.py",
    "content": "print('Hello from file')",
    "title": "创建测试文件"
})

# 读取文件
read_tool = ReadFileTool(user_id=user_id)
content = await read_tool.ainvoke({
    "filename": "test.py",
    "title": "读取测试文件"
})
```

### 异步执行模式

```python
# 使用异步执行模式（需要轮询获取结果）
execute_tool = ExecuteCodeTool(
    user_id="async_user",
    sync_execution=False  # 使用异步模式
)

result = await execute_tool.ainvoke({
    "code": """
def handler(event):
    import time
    time.sleep(5)  # 长时间运行的任务
    return {"status": "completed"}
""",
    "timeout": 60,
    "title": "执行长时间任务"
})
```

### 完整工作流示例

```python
import asyncio
from data_retrieval.tools.sandbox_tools_new import (
    ExecuteCodeTool,
    CreateFileTool,
    ReadFileTool,
    ListFilesTool,
    TerminateSessionTool
)

async def complete_workflow():
    user_id = "workflow_user"
    
    # 1. 创建文件
    create_tool = CreateFileTool(user_id=user_id)
    await create_tool.ainvoke({
        "filename": "data.py",
        "content": "DATA = [1, 2, 3, 4, 5]",
        "title": "创建数据文件"
    })
    
    # 2. 执行代码
    execute_tool = ExecuteCodeTool(user_id=user_id)
    result = await execute_tool.ainvoke({
        "code": """
def handler(event):
    from data import DATA
    return {"sum": sum(DATA), "count": len(DATA)}
""",
        "title": "计算数据总和"
    })
    print(f"执行结果: {result}")
    
    # 3. 列出文件
    list_tool = ListFilesTool(user_id=user_id)
    files = await list_tool.ainvoke({
        "path": "/",
        "title": "列出所有文件"
    })
    print(f"文件列表: {files}")
    
    # 4. 终止会话
    terminate_tool = TerminateSessionTool(user_id=user_id)
    await terminate_tool.ainvoke({
        "title": "清理会话资源"
    })

asyncio.run(complete_workflow())
```

## API 调用

所有工具都支持通过 API 路由调用：

```python
# 使用 as_async_api_cls 方法
result = await ExecuteCodeTool.as_async_api_cls(params={
    "user_id": "api_user",
    "code": "def handler(event): return {'result': 42}",
    "title": "API 调用示例"
})

# 获取 API Schema
schema = await ExecuteCodeTool.get_api_schema()
print(schema["post"]["summary"])  # "execute_code"
```

## 与旧版工具对比

| 特性 | 新版工具 | 旧版工具 (Legacy) |
|-----|---------|------------------|
| API 实现 | RESTful API | SDK |
| 默认模板 | python-basic | 无默认值 |
| 执行模式 | 支持同步/异步 | 仅同步 |
| 会话管理 | 自动创建 | 手动管理 |
| 代码格式 | handler(event) 函数 | 直接执行 |
| API 路径 | `/tools/{tool_name}` | `/tools/{tool_name}_legacy` |

## 注意事项

1. **handler 函数**: 执行代码时需要定义 `handler(event)` 函数，通过 `return` 返回结果
2. **模板**: 默认使用 `python-basic` 模板，支持 pandas、numpy 等常用库
3. **会话**: 如不提供 `user_id`，会自动生成；相同 `user_id` 共享沙箱环境（session_id = `sess-{user_id}`）
4. **超时**: 默认执行超时 30 秒，可通过 `timeout` 参数调整
5. **资源清理**: 使用完毕后建议调用 `TerminateSessionTool` 清理资源
