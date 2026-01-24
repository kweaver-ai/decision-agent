## 1. 背景与问题定义
在 DataAgent 平台中，用户在 Agent 对话过程中需要上传文件供 Agent 分析与操作。为了保证对话的连续性与可复用性，需要一个与 Conversation 绑定的临时文件空间，使 Agent 可以在沙箱内通过稳定路径访问这些文件。

目前缺失的问题：

+ 用户上传的文件无法稳定被 Agent 引用
+ Agent 执行时无法依赖文件路径进行代码执行
+ 文件与 Conversation 的生命周期未被明确绑定
+ 目前缺少对用户可见的临时区能力（上传/列表/下载）

---

## 2. 目标（Goals）
### 2.1 核心目标
1. **提供 Conversation 级别的临时文件空间（Sandbox Workspace）**  
该空间可被 Agent 在沙箱内以稳定路径访问。
2. **支持用户在指定 Agent + Conversation 内上传文件**  
文件将被存储在与沙箱一致的路径结构中。
3. **提供用户可见的文件列表与下载能力**  
用户可在对话界面查看已上传文件并下载。
4. **保证文件生命周期与 Conversation 绑定**  
Conversation 存在 → 文件可引用；Conversation 删除 → 文件立即删除，不可恢复。

---

## 3. 非目标（Non-Goals / Out of Scope）
### 3.1 V1 不支持
1. **跨 Conversation 引用文件**  
不允许跨对话共享或引用历史文件。
2. **目录结构 / 子目录管理**  
V1 文件平铺存储，不支持用户或 Agent 创建子目录。
3. **展示 Agent 生成文件**  
临时区仅展示用户上传文件，不展示 Agent 生成产物。
4. **文件配额策略在 Agent 层暴露**  
文件大小与总容量由 Sandbox Session 层面控制，Agent 不感知配额细节。
5. **Conversation 删除后可恢复**  
删除操作立即生效，文件不可恢复。

---

## 4. 关键概念与约束
### 4.1 Session（Sandbox Session）
**定义**  
Session 是一个 _Sandbox Execution Context_，通常映射为一个 **Kubernetes Pod**，用于承载代码执行、文件系统、工具调用等能力。

**关键不变量**

+ **Session ≠ 用户**
+ Session 是一种 **可复用、可回收的计算资源**
+ 一个 Session 在生命周期内 **只绑定一个 Workspace Root**
+ Session 的创建与销毁具有 **明显调度成本**

**典型特征**

| 属性 | 说明 |
| --- | --- |
| 生命周期 | 显式创建 / 显式销毁 / TTL 回收 |
| 资源 | CPU / Memory / Ephemeral FS |
| 并发 | 支持多个 Conversation 共享 |
| 隔离级别 | 与其他 Session 强隔离 |


---

### 4.2 Conversation
**定义**  
Conversation 表示一次 Agent 对话上下文，是逻辑层概念，不直接映射计算资源。

**设计原则**

+ Conversation **不创建 Pod**
+ Conversation **必须附着在一个已存在的 Session 上**
+ Conversation 之间 **软隔离文件系统**

**隔离模型（Soft Isolation）**

```plain
/workspace/
 └── conversations/
     ├── conv-001/
     ├── conv-002/
     └── conv-003/
```

+ 每个 Conversation 对应一个 **子目录**
+ 默认禁止跨 Conversation 访问
+ 通过配置可显式共享（非默认）

---

### 4.3 Workspace
**定义**  
Workspace 是 Session 内的文件系统可见性边界，用于管理代码、数据、中间产物。

**层级结构**

```plain
Workspace Root
├── shared/              # Session 级共享区（可选）
├── conversations/
│   └── {conversation_id}/
│       ├── input/
│       ├── output/
│       └── tmp/
└── system/
```

**可见性规则**

| 区域 | 可见范围 |
| --- | --- |
| system | Runtime 内部 |
| shared | 同 Session 所有 Conversation |
| conversation dir | 仅当前 Conversation |


### 4.4 作用域与生命周期
+ **Workspace 作用域**：`(agent_id, conversation_id)`
+ **文件生命周期**：绑定 Conversation
    - Conversation 存在 → 文件可用
    - Conversation 删除 → 文件立即删除

### 4.5 文件路径与引用机制
+ 用户上传的文件存储在固定路径：

```plain
/workspace/uploads/temparea/<filename>
```

+ **完整物理路径**（Sandbox Platform 内部）：

```plain
/workspace/uploads/{sandbox_session_id}/{conversation_id}/temparea/<filename>
```

+ **Agent 代码中使用的约定路径**（会被 Sandbox Platform 自动映射）：

```plain
/workspace/uploads/temparea/<filename>
```

+ Agent 在沙箱内必须通过**真实路径**访问文件（而不是 file_id、token 等抽象引用）。
+ 生成文件存储在：

```plain
/workspace/uploads/generated/
```

**不展示给用户**。

### 4.6 目录结构
+ V1 文件平铺存储（flat）
+ 不允许 Agent 或用户创建目录

### 4.7 Agent Prompt 路径注入

为避免 LLM 盲猜路径（如 /data/），必须在 Agent 的 System Prompt 中注入路径前缀：

**注入内容**：
- 临时区根路径：`/workspace/uploads/temparea/`
- 当前可用的文件列表
- 每个文件的完整路径

**注入时机**：每次调用 Agent 时动态注入

**注入示例**：
```
You have access to user-uploaded files in the workspace.
Workspace root: /workspace/uploads/temparea/

Available files:
- data.csv (/workspace/uploads/temparea/data.csv)
- config.json (/workspace/uploads/temparea/config.json)
```

### 4.8 生命周期管理

**文件删除时机**：
1. **主动删除**：用户删除 Conversation 时，DAP 立即调用 Sandbox Platform 删除接口清理文件
2. **被动清理**：Session TTL 过期后，Sandbox Platform 自动清理所有相关文件

**删除一致性保证**：
- Conversation 删除操作必须是同步或可靠异步的
- 删除失败应记录日志但不阻塞 Conversation 删除

### 4.9 代码沙箱安全限制

**Sandbox Platform 必须提供的安全保障**：

#### 1. 文件系统隔离
- Agent 代码只能访问 `/workspace/uploads/temparea/` 目录
- 使用 chroot 或容器级别隔离限制访问范围
- 禁止访问系统目录（`/etc`, `/usr`, `/bin` 等）

#### 2. 命令执行限制
- 禁止 `os.system()`, `subprocess.call()` 等系统调用
- 使用白名单机制，只允许特定的 Python 标准库
- 禁止导入 `os`, `subprocess`, `socket` 等危险模块

#### 3. 资源限制
- CPU/内存/磁盘 IO 限制
- 执行超时时间限制
- 网络访问限制（除非明确需要）

#### 4. 路径验证
- 所有文件操作前验证路径合法性
- 禁止使用 `../` 进行目录遍历
- 禁止符号链接操作

**恶意代码示例及防护**：

```python
# Agent 可能生成的恶意代码
import os
os.system("rm -rf /workspace/uploads/*/")  # ❌ 禁止：命令执行
os.chdir("../../etc")                       # ❌ 禁止：目录遍历
import socket                               # ❌ 禁止：网络访问
```

以上代码应被 Sandbox Platform 的安全机制拦截并拒绝执行。

---

## 5. 用户故事（User Stories）
### 5.1 上传文件
**作为** 用户  
**我希望** 在对话中上传文件  
**以便** Agent 可以读取并基于文件进行分析和处理。

**验收标准**：

+ 用户可以在当前 Conversation 上传文件
+ 文件出现在文件列表中
+ Agent 可以通过路径读取文件

---

### 5.2 查看文件列表
**作为** 用户  
**我希望** 在当前 Conversation 查看已上传文件列表  
**以便** 我确认文件已上传成功，并了解可引用文件。

**验收标准**：

+ 列表展示文件名、大小、上传时间
+ 只展示用户上传文件，不展示 Agent 生成文件

---

### 5.3 下载文件
**作为** 用户  
**我希望** 下载当前 Conversation 上传的文件  
**以便** 我可以保存或进一步处理。

**验收标准**：

+ 支持文件下载
+ 下载文件与上传文件一致

---

### 5.4 Agent 读取文件并执行代码
**作为** Agent  
**我希望** 通过固定路径读取用户上传文件  
**以便** 在沙箱内执行代码并基于文件生成结果。

**验收标准**：

+ Agent 看到的文件路径与沙箱实际路径一致
+ Agent 能在沙箱内读取并处理文件

---

### 5.5 Conversation 删除
**作为** 用户  
**我希望** 删除某个 Conversation  
**以便** 清理该对话相关的临时文件。

**验收标准**：

+ Conversation 删除后，相关 Workspace 文件立即删除
+ 不可恢复

---

## 6. 接口契约（API / SDK / UI）
### 
---

## 7. 安全与权限（简要）
+ 文件只能在对应的 `agent_id + conversation_id` 范围内访问
+ 不允许跨 Conversation 访问
+ 上传、列表、下载接口必须验证用户权限

---

## 8. 关键约束与实现注意点
1. **路径稳定性**  
Agent 必须能稳定访问 `/sandbox/workspace/uploads` 下的文件。
2. **用户可见性**  
文件列表只展示用户上传的文件。
3. **删除强一致性**  
Conversation 删除后，文件必须立即删除。
4. **容量限制**  
由 Sandbox Session 控制，Agent 不感知。

---

## 
