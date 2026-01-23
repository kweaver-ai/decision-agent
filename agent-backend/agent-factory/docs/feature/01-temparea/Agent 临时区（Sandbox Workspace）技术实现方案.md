## 0. 目标与范围（再次明确）

### 0.1 核心目标
在 **Decision Agent Platform** 中实现 **Agent 临时区（Sandbox Workspace）**，用于：

1. 用户在指定 Agent + Conversation 下上传文件（通过 Sandbox Platform 接口）
2. 用户可查看文件列表、下载文件（通过 Sandbox Platform 接口）
3. Agent 在对话中基于文件路径生成代码并在 Sandbox Platform 内执行
4. Agent 与 Sandbox 的交互由 **算子平台注册的工具**完成
5. 整个过程采用 **LLM React loop**，支持流式输出

### 0.2 约束
+ 文件作用域：`(agent_id, conversation_id)`
+ 文件路径必须是 **真实沙箱路径**（Agent 生成的代码必须可执行）
+ 仅展示用户上传文件（Agent 生成文件不展示）
+ Conversation 删除立即清理文件，不可恢复
+ 跨 Conversation 文件引用不支持
+ 存储与沙箱内部对象存储不暴露给外部系统

---

# 1. C4 架构设计（概念级）

## 1.1 Context 图

```mermaid
graph TD
  User["User (Browser/SDK)"]
  DAP[Decision Agent Platform]
  OP[Operator Platform]
  SP[Sandbox Platform]

  User -->|Agent Conversation UI| DAP
  DAP -->|Invoke Tools| OP
  OP -->|Workspace/Execution APIs| SP

  SP -->|Internal Object Storage| SPStorage[Sandbox Internal Storage]
  SP -->|Internal Metadata DB| SPDB[Metadata DB]
```

**Decision Agent Platform（DAP）**

+ 负责 Agent 对话与 React Loop
+ 负责与 Operator Platform 交互
+ 管理 Sandbox Session 生命周期（直接调用 Sandbox Platform）
+ 在 Chat 流程中自动检查/创建 Sandbox Session

**Operator Platform（OP）**

+ 工具注册中心（Tool Registry）
+ 代理工具调用（Invoke）
+ 将沙箱能力封装成工具，供 DAP 调用

**Sandbox Platform（SP）**

+ 负责 Session、Execution、File Upload/List/Download（接口已存在）
+ 对外暴露的能力只通过接口，不暴露内部存储

---

## 1.2 Container 图

```mermaid
graph TD
  subgraph DAP [Decision Agent Platform]
    DAP_API[API Gateway / Frontend]
    DAP_Conv[Conversation Service]
    DAP_Agent["Agent Orchestrator (LLM React Loop)"]
  end

  subgraph OP [Operator Platform]
    OP_Reg[Tool Registry]
    OP_Invoke[Tool Invocation]
    OP_Auth[Tool Auth & Permission]
  end

  subgraph SP [Sandbox Platform]
    SP_Work["Workspace Service (upload/list/download)"]
    SP_Exec[Execution Service]
    SP_Internal["Internal Storage (hidden)"]
    SP_DB[Metadata DB]
  end

  User["User (Browser/SDK)"]

  %% User interactions
  User -->|Open Agent UI| DAP_API
  User -->|Upload/List/Download files| SP_Work

  %% DAP internal flows
  DAP_API --> DAP_Conv
  DAP_Conv --> DAP_Agent

  %% DAP -> OP tool calls
  DAP_Agent -->|"tool call (with sandbox_session_id)"| OP_Invoke
  OP_Invoke --> OP_Reg
  OP_Invoke -->|call SP execution API| SP_Exec

  %% SP internal dependencies
  SP_Work --> SP_DB
  SP_Work --> SP_Internal
  SP_Exec --> SP_DB
  SP_Exec --> SP_Internal
```

---

## 1.3 Chat 流程中 Sandbox Session 管理图

```mermaid
sequenceDiagram
    participant User as User (Browser)
    participant DAP as Decision Agent Platform
    participant SP as Sandbox Platform
    participant OP as Operator Platform

    User->>DAP: Chat Request (user_id, agent_id, conversation_id)
    
    Note over DAP: 生成 session_id = sb-session-{user_id}-{agent_id}
    
    Note over DAP,SP: 1. 检测 Sandbox Session 状态
    DAP->>SP: GET /api/v1/sessions/{session_id}
    
    alt Session 存在且 running
        SP-->>DAP: Session Info (status=running)
        Note over DAP: 复用现有 Session
    else Session 不存在 (404)
        Note over DAP,SP: 2. 创建新 Session
        DAP->>SP: POST /api/v1/sessions (user_id, agent_id)
        SP-->>DAP: Create Response (session_id, status=pending)
        
        Note over DAP,SP: 3. 等待 Session 就绪
        loop Poll until running (max 30 times)
            DAP->>SP: GET /api/v1/sessions/{session_id}
            SP-->>DAP: Session Status
        end
    else Session 异常/非 running (error/stopped)
        SP-->>DAP: Session Info (status!=running)
        Note over DAP,SP: 4. 自动重新创建 Session
        DAP->>SP: POST /api/v1/sessions (user_id, agent_id)
        SP-->>DAP: Create Response (new session_id, status=pending)
        
        loop Poll until running (max 30 times)
            DAP->>SP: GET /api/v1/sessions/{new_session_id}
            SP-->>DAP: Session Status
        end
    end

    Note over DAP,OP: 5. 调用 Agent Executor
    DAP->>OP: Call Agent Executor (with sandbox_session_id)
    OP->>SP: Execute Code (with sandbox_session_id)
    SP-->>OP: Stream Result
    OP-->>DAP: Stream Result

    DAP-->>User: Stream Response (SSE)
```

---

# 2. 核心概念设计

## 2.1 Sandbox Session（用户沙箱会话）

### 定义

每个用户在每个 Agent 下有且只有一个 Sandbox Session，Session 跟随用户生命周期。

### Session ID 生成规则

- **格式**：`sb-session-{user_id}-{agent_id}`
- **示例**：`sb-session-user123-agent456`
- **固定性**：同一用户的同一 Agent 始终使用相同的 Session ID
- **无需缓存**：每次 Chat 都基于 `user_id` 和 `agent_id` 生成相同的 Session ID

### 生命周期管理

1. **检测时机**：用户发起 Chat 请求时
2. **检测方式**：调用 Sandbox Platform API 直接检测 Session 状态
3. **自动创建**：如果 Session 不存在或异常，自动创建新 Session
4. **等待就绪**：创建新 Session 后，轮询等待状态变为 `running`
5. **复用逻辑**：如果 Session 存在且状态为 `running`，直接复用

### 无需持久化存储

- 不使用数据库存储 Session 映射关系
- 不使用 Redis 缓存
- 不使用 sync.Map 内存缓存
- Session ID 直接由 `user_id` 和 `agent_id` 生成，每次都相同

---

## 2.2 Workspace File（临时区文件）

### 文件路径结构（Sandbox Platform 内部）

```
/workspace/
└── uploads/
    └── {sandbox_session_id}/
        └── {conversation_id}/
            └── temparea/              # 【新增】临时区上传的文件目录
                ├── data.csv
                ├── model.pkl
                └── config.json
```

### 路径说明

| 路径层级 | 说明 |
|---------|------|
| `uploads` | Sandbox Platform 固定目录 |
| `{sandbox_session_id}` | Sandbox Platform 返回的 Session ID |
| `{conversation_id}` | Conversation ID |
| `temparea` | **固定目录名**，用于区分用户上传文件与其他类型文件 |
| `*.csv, *.pkl, ...` | 用户上传的文件 |

### Agent 代码引用示例

```python
# Agent 生成的代码中引用用户上传的文件
import pandas as pd

# Sandbox Platform 会根据 sandbox_session_id 和 conversation_id 自动映射路径
# Agent 只需要使用约定路径即可
df = pd.read_csv('/workspace/uploads/temparea/data.csv')
```

---

# 3. 核心流程设计

## 3.1 Chat 流程中集成 Sandbox Session 管理

### 关键代码位置

在 `src/domain/service/agentrunsvc/chat.go` 的 `Chat` 函数中，第 122-126 行（HandleGetInfoOrCreate 之后）添加：

```go
// NOTE: 确保 Sandbox Session 存在并就绪
sessionID := fmt.Sprintf("sb-session-%s-%s", req.UserID, req.AgentID)
sandboxSessionID, err := agentSvc.EnsureSandboxSession(ctx, sessionID, req)
if err != nil {
    o11y.Error(newCtx, fmt.Sprintf("[chat] ensure sandbox session failed: %v", err))
    return nil, err
}

// 将 sandbox_session_id 传递给 Agent Executor
req.SandboxSessionID = sandboxSessionID
```

---

## 3.2 EnsureSandboxSession 函数实现

### 完整实现

```go
// 在 src/domain/service/agentrunsvc/ensure_sandbox_session.go 中新增

package agentsvc

import (
    "context"
    "fmt"
    "time"

    "github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/httpaccess/sandboxplatformhttp/sandboxplatformdto"
    agentreq "github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/agent/req"
    o11y "github.com/kweaver-ai/kweaver-go-lib/observability"
    "github.com/pkg/errors"
)

// EnsureSandboxSession 确保 Sandbox Session 存在并就绪
// 完全移除 sync.Map 缓存，每次直接调用 Sandbox Platform 检测
func (s *agentSvc) EnsureSandboxSession(ctx context.Context, sessionID string, req *agentreq.ChatReq) (string, error) {
    ctx, _ = o11y.StartInternalSpan(ctx)
    defer o11y.EndSpan(ctx, nil)

    o11y.SetAttributes(ctx,
        o11y.String("session_id", sessionID),
        o11y.String("user_id", req.UserID),
        o11y.String("agent_id", req.AgentID),
    )

    // 1. 检测 Session 状态
    sessionInfo, err := s.sandboxPlatform.GetSession(ctx, sessionID)
    if err != nil {
        // 404 错误表示 Session 不存在，继续创建
        if s.isSessionNotFoundError(err) {
            o11y.SetAttributes(ctx, o11y.String("action", "create_new"))
            return s.createNewSession(ctx, sessionID, req)
        }
        
        // 其他错误：尝试创建新 Session
        o11y.SetAttributes(ctx, o11y.String("action", "recover_from_error"))
        s.logger.Warnf("[EnsureSandboxSession] get session failed: %v, will create new session", err)
        return s.createNewSession(ctx, sessionID, req)
    }

    // 2. 检查 Session 状态
    if sessionInfo.Status == "running" {
        o11y.SetAttributes(ctx, o11y.String("action", "reuse_existing"))
        s.logger.Infof("[EnsureSandboxSession] reuse existing session: %s", sessionID)
        return sessionID, nil
    }

    // 3. Session 状态非 running，自动重新创建
    o11y.SetAttributes(ctx, o11y.String("action", "recreate"))
    s.logger.Warnf("[EnsureSandboxSession] session status is %s, will recreate: %s", sessionInfo.Status, sessionID)
    return s.createNewSession(ctx, sessionID, req)
}

// createNewSession 创建新的 Sandbox Session
func (s *agentSvc) createNewSession(ctx context.Context, sessionID string, req *agentreq.ChatReq) (string, error) {
    createReq := sandboxplatformdto.CreateSessionReq{
        UserID:           req.UserID,
        AgentID:          req.AgentID,
        BusinessDomainID: req.XBusinessDomainID,
        Config: map[string]interface{}{
            "session_id": sessionID, // 使用预生成的 session_id
            "file_upload_config": map[string]interface{}{
                "max_file_size":      s.sandboxPlatformConf.DefaultFileUploadConfig.MaxFileSize,
                "max_file_size_unit": s.sandboxPlatformConf.DefaultFileUploadConfig.MaxFileSizeUnit,
                "max_file_count":     s.sandboxPlatformConf.DefaultFileUploadConfig.MaxFileCount,
                "allowed_file_types": s.sandboxPlatformConf.DefaultFileUploadConfig.AllowedFileTypes,
            },
        },
    }

    createResp, err := s.sandboxPlatform.CreateSession(ctx, createReq)
    if err != nil {
        s.logger.Errorf("[createNewSession] create failed: %v", err)
        return "", errors.Wrap(err, "create sandbox session failed")
    }

    // 使用返回的 session_id（可能与请求的预生成 ID 不同）
    actualSessionID := createResp.SessionID
    if createResp.SessionID == "" {
        actualSessionID = sessionID
    }

    // 等待 Session 就绪（轮询）
    sessionReady := false
    maxRetries := s.sandboxPlatformConf.MaxRetries
    retryInterval := s.sandboxPlatformConf.RetryInterval

    for i := 0; i < maxRetries; i++ {
        sessionInfo, err := s.sandboxPlatform.GetSession(ctx, actualSessionID)
        if err != nil {
            s.logger.Errorf("[createNewSession] get session status failed (attempt %d): %v", i+1, err)
            time.Sleep(retryInterval)
            continue
        }

        if sessionInfo.Status == "running" {
            sessionReady = true
            s.logger.Infof("[createNewSession] session ready: %s (attempts: %d)", actualSessionID, i+1)
            break
        }

        time.Sleep(retryInterval)
    }

    if !sessionReady {
        s.logger.Errorf("[createNewSession] session not ready after %d retries", maxRetries)
        return "", errors.New("sandbox session not ready after retries")
    }

    return actualSessionID, nil
}

// isSessionNotFoundError 判断是否为 Session 不存在的错误
func (s *agentSvc) isSessionNotFoundError(err error) bool {
    // 根据实际 HTTP 客户端的错误类型判断
    // 例如：检查 HTTP 状态码是否为 404
    return false // 实现根据具体情况调整
}
```

---

# 4. DDD 层次设计（简化版）

## 4.1 目录结构

```
src/
├── drivenadapter/
│   └── httpaccess/
│       └── sandboxplatformhttp/
│           ├── define.go
│           ├── create_session.go
│           ├── get_session.go
│           └── delete_session.go
└── domain/service/
    └── agentrunsvc/
        ├── chat.go
        ├── ensure_sandbox_session.go  # 【新增】
        ├── common.go
        └── define.go
```

---

## 4.2 Sandbox Platform HTTP 客户端

### 接口定义

**port/driven/ihttpaccess/isandboxplatformhttp/sandbox_platform.go**：

```go
package isandboxplatformhttp

import (
    "context"
    sandboxdto "github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/httpaccess/sandboxplatformhttp/sandboxplatformdto"
)

// ISandboxPlatform Sandbox Platform 接口
type ISandboxPlatform interface {
    // CreateSession 创建 Sandbox Session
    CreateSession(ctx context.Context, req sandboxdto.CreateSessionReq) (*sandboxdto.CreateSessionResp, error)
    // GetSession 获取 Sandbox Session 信息
    GetSession(ctx context.Context, sessionID string) (*sandboxdto.GetSessionResp, error)
    // DeleteSession 删除 Sandbox Session
    DeleteSession(ctx context.Context, sessionID string) error
}
```

---

### DTO 定义

**drivenadapter/httpaccess/sandboxplatformhttp/sandboxplatformdto/req.go**：

```go
package sandboxplatformdto

// CreateSessionReq 创建 Session 请求
type CreateSessionReq struct {
    UserID           string                 `json:"user_id"`
    AgentID          string                 `json:"agent_id"`
    BusinessDomainID string                 `json:"business_domain_id"`
    Config           map[string]interface{} `json:"config,omitempty"`
}
```

**drivenadapter/httpaccess/sandboxplatformhttp/sandboxplatformdto/resp.go**：

```go
package sandboxplatformdto

// CreateSessionResp 创建 Session 响应
type CreateSessionResp struct {
    SessionID string                 `json:"session_id"`
    Status    string                 `json:"status"`
    CreatedAt int64                  `json:"created_at"`
    TTL       int64                  `json:"ttl"`
    Info      map[string]interface{} `json:"info,omitempty"`
}

// GetSessionResp 获取 Session 响应
type GetSessionResp struct {
    SessionID string `json:"session_id"`
    Status    string `json:"status"` // pending/running/stopped
    CreatedAt int64  `json:"created_at"`
    TTL       int64  `json:"ttl"`
}
```

---

### HTTP 客户端实现

**drivenadapter/httpaccess/sandboxplatformhttp/create_session.go**：

```go
package sandboxplatformhttp

import (
    "context"
    "fmt"

    sandboxdto "github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/httpaccess/sandboxplatformhttp/sandboxplatformdto"
    "github.com/kweaver-ai/decision-agent/agent-factory/conf"
    "github.com/kweaver-ai/decision-agent/agent-factory/src/infra/cmp/httpclient"
    "github.com/kweaver-ai/decision-agent/agent-factory/src/infra/cmp/icmp"
    "github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cutil"
    o11y "github.com/kweaver-ai/kweaver-go-lib/observability"
    "github.com/pkg/errors"
)

func (svc *sandboxPlatformHttpAcc) CreateSession(ctx context.Context, req sandboxdto.CreateSessionReq) (*sandboxdto.CreateSessionResp, error) {
    ctx, _ = o11y.StartInternalSpan(ctx)
    defer o11y.EndSpan(ctx, nil)

    url := fmt.Sprintf("%s/api/v1/sessions",
        cutil.GetHTTPAccess(svc.sandboxPlatformConf.Svc.Host, svc.sandboxPlatformConf.Svc.Port, svc.sandboxPlatformConf.Svc.Protocol))

    var resp sandboxdto.CreateSessionResp
    err := svc.httpClient.Post(ctx, url, req, &resp)
    if err != nil {
        return nil, errors.Wrap(err, "create sandbox session failed")
    }

    return &resp, nil
}
```

**drivenadapter/httpaccess/sandboxplatformhttp/get_session.go**：

```go
package sandboxplatformhttp

import (
    "context"
    "fmt"

    sandboxdto "github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/httpaccess/sandboxplatformhttp/sandboxplatformdto"
    "github.com/kweaver-ai/decision-agent/agent-factory/src/infra/cmp/httpclient"
    o11y "github.com/kweaver-ai/kweaver-go-lib/observability"
    "github.com/pkg/errors"
)

func (svc *sandboxPlatformHttpAcc) GetSession(ctx context.Context, sessionID string) (*sandboxdto.GetSessionResp, error) {
    ctx, _ = o11y.StartInternalSpan(ctx)
    defer o11y.EndSpan(ctx, nil)

    url := fmt.Sprintf("%s/api/v1/sessions/%s",
        svc.sandboxPlatformConf.BaseURL, sessionID)

    var resp sandboxdto.GetSessionResp
    err := svc.httpClient.Get(ctx, url, nil, &resp)
    if err != nil {
        return nil, errors.Wrap(err, "get sandbox session failed")
    }

    return &resp, nil
}
```

**drivenadapter/httpaccess/sandboxplatformhttp/define.go**：

```go
package sandboxplatformhttp

import (
    "sync"

    "github.com/kweaver-ai/decision-agent/agent-factory/conf"
    "github.com/kweaver-ai/decision-agent/agent-factory/src/infra/cmp/httpclient"
    "github.com/kweaver-ai/decision-agent/agent-factory/src/infra/cmp/icmp"
    "github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cutil"
)

type sandboxPlatformHttpAcc struct {
    logger                icmp.Logger
    httpClient            httpclient.HTTPClient
    sandboxPlatformConf   *conf.SandboxPlatformConf
    baseURL              string
}

var (
    sandboxPlatformOnce sync.Once
    sandboxPlatformImpl ISandboxPlatform
)

func NewSandboxPlatformHttpAcc(sandboxPlatformConf *conf.SandboxPlatformConf, httpClient httpclient.HTTPClient, logger icmp.Logger) ISandboxPlatform {
    sandboxPlatformOnce.Do(func() {
        sandboxPlatformImpl = &sandboxPlatformHttpAcc{
            logger:              logger,
            httpClient:          httpClient,
            sandboxPlatformConf:  sandboxPlatformConf,
            baseURL:             cutil.GetHTTPAccess(sandboxPlatformConf.Svc.Host, sandboxPlatformConf.Svc.Port, sandboxPlatformConf.Svc.Protocol),
        }
    })
    return sandboxPlatformImpl
}
```

---

# 5. 配置设计

## 5.1 Sandbox Platform 配置

**conf/sandbox_platform.go**：

```go
package conf

import "github.com/kweaver-ai/decision-agent/agent-factory/cconf"

// SandboxPlatformConf Sandbox Platform 配置
type SandboxPlatformConf struct {
    SvcConf                      cconf.SvcConf      `yaml:"svc"`
    DefaultTTL                   int64               `yaml:"default_ttl"`     // 默认 Session TTL（秒）
    MaxRetries                   int                 `yaml:"max_retries"`     // 等待 Session 就绪的最大重试次数
    RetryInterval                string              `yaml:"retry_interval"`  // 重试间隔（如 "500ms"）
    DefaultFileUploadConfig      FileUploadConfig    `yaml:"file_upload_config"`
}

// FileUploadConfig 文件上传配置
type FileUploadConfig struct {
    MaxFileSize      int64    `yaml:"max_file_size"`      // 最大文件大小（数值）
    MaxFileSizeUnit  string   `yaml:"max_file_size_unit"` // 单位：KB/MB/GB
    MaxFileCount     int      `yaml:"max_file_count"`     // 最大文件数量
    AllowedFileTypes []string `yaml:"allowed_file_types"` // 允许的文件类型
}
```

---

## 5.2 配置文件示例

**agent-factory.yaml**：

```yaml
sandbox_platform:
  svc:
    host: "sandbox-platform.kweaver.svc.cluster.local"
    port: 9100
    protocol: "http"
  default_ttl: 7200              # 默认 2 小时
  max_retries: 30                 # 最多重试 30 次
  retry_interval: "500ms"         # 每次间隔 500ms
  file_upload_config:
    max_file_size: 100
    max_file_size_unit: "MB"
    max_file_count: 50
    allowed_file_types:
      - "csv"
      - "xlsx"
      - "json"
      - "txt"
      - "pkl"
      - "png"
      - "jpg"
      - "pdf"
```

---

# 6. 前端集成指南

## 6.1 前端如何获取 Sandbox Session ID

### Session ID 生成规则

Session ID 基于 `user_id` 和 `agent_id` 生成，前后端使用相同的规则即可：

```typescript
// 前端生成 Session ID
function generateSessionId(userId: string, agentId: string): string {
    return `sb-session-${userId}-${agentId}`;
}

// 示例
const sessionId = generateSessionId('user123', 'agent456');
// 结果: "sb-session-user123-agent456"
```

### 使用方式

前端在上传文件时，使用相同的 Session ID 生成规则即可：

```typescript
// 上传文件
async function uploadFile(userId: string, agentId: string, conversationId: string, file: File) {
    const sessionId = generateSessionId(userId, agentId);
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('conversation_id', conversationId);
    formData.append('subdir', 'temparea');
    
    const response = await fetch(
        `${SANDBOX_API_URL}/api/v1/sessions/${sessionId}/files/upload`,
        {
            method: 'POST',
            body: formData,
        }
    );
    
    return response.json();
}
```

### 关键要点

- **无需从 Decision Agent 获取 Session ID**
- **前后端使用相同的生成规则**
- **格式**：`sb-session-{user_id}-{agent_id}`
- **固定性**：同一用户的同一 Agent 始终使用相同的 Session ID

---

## 6.2 上传文件到 Sandbox

```typescript
interface UploadFileOptions {
  sandboxSessionId: string;
  conversationId: string;
  file: File;
}

async function uploadFile(options: UploadFileOptions): Promise<any> {
  const { sandboxSessionId, conversationId, file } = options;
  const formData = new FormData();
  formData.append('file', file);
  formData.append('conversation_id', conversationId);
  formData.append('subdir', 'temparea'); // 指定子目录为 temparea

  const response = await fetch(
    `${SANDBOX_API_URL}/api/v1/sessions/${sandboxSessionId}/files/upload`,
    {
      method: 'POST',
      body: formData,
    }
  );

  if (!response.ok) {
    throw new Error(`Upload failed: ${response.statusText}`);
  }

  return response.json();
}

// 使用示例
const sandboxSessionId = await chatWithSandboxSession('agent123', '上传一个文件分析');

await uploadFile({
  sandboxSessionId: sandboxSessionId,
  conversationId: 'conv456',
  file: selectedFile,
});
```

---

## 6.3 列出临时区文件

```typescript
interface ListFilesOptions {
  sandboxSessionId: string;
  conversationId: string;
}

async function listTempAreaFiles(options: ListFilesOptions): Promise<string[]> {
  const { sandboxSessionId, conversationId } = options;

  const response = await fetch(
    `${SANDBOX_API_URL}/api/v1/sessions/${sandboxSessionId}/files`,
    {
      method: 'GET',
      headers: {
        'conversation_id': conversationId,
        'subdir': 'temparea', // 只列出 temparea 目录下的文件
      },
    }
  );

  if (!response.ok) {
    throw new Error(`List files failed: ${response.statusText}`);
  }

  const data = await response.json();
  return data.files; // ["data.csv", "model.pkl", ...]
}

// 使用示例
const files = await listTempAreaFiles({
  sandboxSessionId: sandboxSessionId,
  conversationId: 'conv456',
});

console.log('Uploaded files:', files);
```

---

## 6.4 下载文件

```typescript
interface DownloadFileOptions {
  sandboxSessionId: string;
  fileName: string;
}

async function downloadFile(options: DownloadFileOptions): Promise<void> {
  const { sandboxSessionId, fileName } = options;

  const response = await fetch(
    `${SANDBOX_API_URL}/api/v1/sessions/${sandboxSessionId}/files/${fileName}`,
    {
      method: 'GET',
    }
  );

  if (!response.ok) {
    throw new Error(`Download failed: ${response.statusText}`);
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = fileName;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
}

// 使用示例
await downloadFile({
  sandboxSessionId: sandboxSessionId,
  fileName: 'data.csv',
});
```

---

# 7. Agent 代码执行集成

## 7.1 传递 Sandbox Session ID 给 Agent Executor

### 修改 ChatReq DTO

**driveradapter/api/rdto/agent/req/chat_req.go**：

```go
type ChatReq struct {
    // ... 现有字段 ...

    // SandboxSessionID Sandbox Session ID（新增）
    SandboxSessionID string `json:"sandbox_session_id"`
}
```

### 修改 GenerateAgentCallReq 函数

**domain/service/agentrunsvc/chat_req.go**：

在 `GenerateAgentCallReq` 函数中，添加 Sandbox Session ID 到请求参数：

```go
func (agentSvc *agentSvc) GenerateAgentCallReq(
    ctx context.Context,
    req *agentreq.ChatReq,
    contexts []*comvalobj.LLMMessage,
    agent *agentfactorydto.Agent,
) (*v2agentexecutordto.V2AgentCallReq, error) {
    // ... 现有代码 ...

    agentCallReq := v2agentexecutordto.V2AgentCallReq{
        // ... 其他字段 ...
        SandboxSessionID: req.SandboxSessionID, // 新增
    }

    return agentCallReq, nil
}
```

---

## 7.2 Agent Executor 使用 Sandbox Session ID

Agent Executor 在调用 Sandbox Platform 代码执行工具时，自动使用传递的 `sandbox_session_id`，确保在正确的 Session 环境中执行代码。

### Agent 代码示例

```python
# Agent 生成的代码中引用用户上传的文件
import pandas as pd

# 文件路径格式：/workspace/uploads/temparea/{filename}
# Sandbox Platform 会根据 sandbox_session_id 和 conversation_id 自动映射路径
# Agent 只需要使用约定路径即可

# 读取用户上传的文件
df = pd.read_csv('/workspace/uploads/temparea/data.csv')
print(df.head())

# 处理数据
result = df.describe()

# Agent 生成结果文件（可选，不在 temparea 目录）
with open('/workspace/uploads/result.json', 'w') as f:
    f.write(result.to_json())
```

### 路径映射说明

Sandbox Platform 内部会自动进行路径映射：

| Agent 使用的路径 | Sandbox Platform 实际路径 |
|----------------|--------------------------|
| `/workspace/uploads/temparea/data.csv` | `/workspace/uploads/{sandbox_session_id}/{conversation_id}/temparea/data.csv` |

Agent 无需知道完整的物理路径，只需使用约定路径即可。

---

# 8. 关键实现注意点

## 8.1 并发控制

### 无需并发控制

由于完全移除缓存机制，不再需要处理并发创建 Session 的场景：

- **Session ID 固定**：同一用户的同一 Agent 始终使用相同的 Session ID
- **直接检测状态**：每次 Chat 都调用 Sandbox Platform API 检测
- **自动处理冲突**：如果多个请求同时检测到 Session 不存在，都会调用创建 API
  - Sandbox Platform 负责处理并发创建（幂等性）
  - 如果 Session 已存在，创建 API 可能返回错误或返回已存在的 Session ID
  - Decision Agent 继续轮询等待 Session 就绪即可

### Sandbox Platform 需保证的幂等性

Sandbox Platform 的 `POST /api/v1/sessions` API 应该保证：
- 如果 `session_id` 已存在且状态正常，返回现有 Session 信息
- 如果 `session_id` 不存在，创建新 Session
- 如果 `session_id` 存在但状态异常，可以选择：
  - 返回错误，由 Decision Agent 重新创建（使用新的 session_id）
  - 自动恢复 Session 到可用状态

---

## 8.2 错误处理

### Sandbox Platform 创建失败

```go
createResp, err := s.sandboxPlatform.CreateSession(ctx, createReq)
if err != nil {
    o11y.Error(ctx, fmt.Sprintf("[EnsureSandboxSession] create failed: %v", err))
    return "", rest.NewHTTPError(ctx, http.StatusInternalServerError,
        apierr.AgentAPP_SandboxSessionCreateFailed).
        WithErrorDetails("Failed to create sandbox session")
}
```

### Session 就绪超时

```go
if !sessionReady {
    o11y.Error(ctx, "[EnsureSandboxSession] session not ready after retries")
    return "", rest.NewHTTPError(ctx, http.StatusServiceUnavailable,
        apierr.AgentAPP_SandboxSessionNotReady).
        WithErrorDetails("Sandbox session initialization timeout")
}
```

### 轮询验证失败

```go
sessionInfo, err := s.sandboxPlatform.GetSession(ctx, sessionID)
if err != nil {
    o11y.Error(ctx, fmt.Sprintf("[EnsureSandboxSession] get session failed: %v", err))
    // 继续执行，尝试创建新 Session
}
```

---

## 8.3 日志与追踪

### OpenTelemetry 追踪

```go
func (s *agentSvc) EnsureSandboxSession(ctx context.Context, sessionID string, req *agentreq.ChatReq) (string, error) {
    ctx, _ = o11y.StartInternalSpan(ctx)
    defer o11y.EndSpan(ctx, nil)

    // 设置属性
    o11y.SetAttributes(ctx,
        o11y.String("session_id", sessionID),
        o11y.String("user_id", req.UserID),
        o11y.String("agent_id", req.AgentID),
        o11y.String("business_domain_id", req.XBusinessDomainID),
    )

    // ... 执行逻辑 ...

    return sessionID, nil
}
```

### 关键日志

```go
// 复用现有 Session
s.logger.Infof("[EnsureSandboxSession] reuse existing session: %s", sessionID)

// 创建新 Session
s.logger.Infof("[EnsureSandboxSession] create new sandbox session: %s", createResp.SessionID)

// Session 就绪
s.logger.Infof("[EnsureSandboxSession] sandbox session ready: %s (attempts: %d)", sessionID, attempts)
```

---

## 8.4 清理策略

### 无需主动清理

由于不使用任何缓存机制，无需主动清理 Session 映射：

- **无缓存**：不使用 sync.Map、Redis、数据库存储 Session 信息
- **无清理**：Session 清理由 Sandbox Platform 的 TTL 机制负责
- **无泄漏风险**：应用重启不影响，因为没有任何持久化状态

### Sandbox Platform 的清理责任

- Session TTL 过期后自动清理
- Session 达到资源限制时自动清理
- 支持手动删除 Session API（如果需要）

---

# 9. 实施步骤

## 阶段一：基础设施准备

1. 创建 Sandbox Platform HTTP 客户端接口和实现
2. 添加 Sandbox Platform 配置
3. 更新依赖注入

---

## 阶段二：核心逻辑实现

1. 实现 `EnsureSandboxSession` 函数
2. 在 Chat 流程中集成 Sandbox Session 检查/创建
3. 修改 `GenerateAgentCallReq` 传递 `sandbox_session_id`
4. 添加错误处理和日志

---

## 阶段三：测试验证

1. 单元测试：`EnsureSandboxSession` 函数
2. 集成测试：Chat 流程中 Sandbox Session 管理
3. 并发测试：多请求并发创建 Session
4. 端到端测试：文件上传 + Agent 执行

---

## 阶段四：前端集成

1. 前端从 Chat 响应中获取 Sandbox Session ID
2. 实现文件上传/列表/下载功能
3. 确保文件路径正确（`temparea` 子目录）

---

## 阶段五：清理旧代码

1. 删除旧的 temparea 相关代码（如果存在）
2. 删除 `t_data_agent_temporary_area` 表（如果不再使用）
3. 更新单元测试
4. 更新文档

---

# 10. 总结

### 核心设计原则

1. **简化优先**：不依赖任何缓存机制（无 Redis、无 sync.Map、无数据库）
2. **无侵入性**：不新增 Decision Agent API 接口
3. **自动管理**：在 Chat 流程中自动检查/创建 Sandbox Session
4. **路径约定**：使用 `temparea` 子目录区分用户上传文件
5. **容错设计**：创建失败、就绪超时等场景均有处理

### 关键技术点

- **固定 Session ID**：基于 `user_id` 和 `agent_id` 生成
- **直接检测状态**：每次调用 Sandbox Platform API 检测
- **自动重新创建**：Session 不存在或异常时自动创建
- **轮询等待就绪**：创建后轮询等待 Session 状态变为 `running`
- **Agent Executor 传递**：将 `sandbox_session_id` 传递给 Agent Executor
- **Sandbox Platform 路径映射**：根据 session_id 和 conversation_id 自动映射

### 扩展性考虑

- 可选：用户登出时清理 Sandbox Session（调用 Sandbox Platform 删除 API）
- 可选：支持 Session 配置自定义（通过 config 参数）
- 可选：添加 Session 状态监控和告警
