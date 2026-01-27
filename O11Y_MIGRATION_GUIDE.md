# OpenTelemetry 迁移指南

本文档说明如何将代码从 `kweaver-go-lib/observability` (o11y) 迁移到开源 OpenTelemetry SDK。

## 📊 迁移状态

| 组件 | 状态 | 说明 |
|-----|------|------|
| OpenTelemetry Logger | ✅ 已实现 | `src/infra/opentelemetry/logs/logger.go` |
| OpenTelemetry Trace | ✅ 已实现 | `src/infra/opentelemetry/trace/trace.go` |
| 辅助工具函数 | ✅ 已实现 | `src/infra/opentelemetry/otel_helper.go` |
| HTTP 中间件 | ✅ 已迁移 | `src/infra/common/capimiddleware/o11y_trace.go` |
| chat.go | ✅ 已迁移 | `src/domain/service/agentrunsvc/chat.go` |
| conversation handler | ✅ 示例完成 | `src/driveradapter/api/httphandler/conversationhandler/` |
| 其他文件 | ⏳ 待迁移 | ~95+ 文件需要迁移 |

## 🔄 API 迁移映射

### 日志记录

| 旧 API (o11y) | 新 API (OpenTelemetry) | 说明 |
|--------------|----------------------|------|
| `o11y.Error(ctx, msg)` | `otelHelper.Error(ctx, msg)` | 记录错误日志 |
| `o11y.Error(ctx, fmt.Sprintf(...))` | `otelHelper.Errorf(ctx, format, args...)` | 格式化错误日志 |
| `o11y.Info(ctx, msg)` | `otelHelper.Info(ctx, msg)` | 记录信息日志 |
| `o11y.Warn(ctx, msg)` | `otelHelper.Warn(ctx, msg)` | 记录警告日志 |
| `o11y.Debug(ctx, msg)` | `otelHelper.Debug(ctx, msg)` | 记录调试日志 |

### 追踪

| 旧 API (o11y) | 新 API (OpenTelemetry) | 说明 |
|--------------|----------------------|------|
| `o11y.StartServerSpan(c)` | `otelTrace.StartServerSpan(c)` | 创建服务器 span |
| `o11y.SetAttributes(ctx, attrs)` | `otelTrace.SetAttributes(ctx, attrs)` | 设置 span 属性 |
| `o11y.EndSpan(ctx, err)` | `otelTrace.EndSpan(ctx, err)` | 结束 span |

## 📝 迁移步骤

### 1. 导入包替换

**之前:**
```go
import (
    o11y "github.com/kweaver-ai/kweaver-go-lib/observability"
)
```

**之后:**
```go
import (
    otelHelper "github.com/kweaver-ai/decision-agent/agent-factory/src/infra/opentelemetry"
)
```

### 2. 错误日志替换

**之前:**
```go
o11y.Error(ctx, fmt.Sprintf("[Update] failed: %v", err))
```

**之后:**
```go
otelHelper.Errorf(ctx, "[Update] failed: %v", err)
```

### 3. HTTP Handler 示例

完整的 HTTP handler 迁移示例:

```go
// 之前
func (h *handler) Update(c *gin.Context) {
    if err := c.ShouldBindJSON(&req); err != nil {
        h.logger.Errorf("[Update] bind error: %v", err)
        o11y.Error(c, fmt.Sprintf("[Update] bind error: %v", err))
        return
    }
}

// 之后
func (h *handler) Update(c *gin.Context) {
    if err := c.ShouldBindJSON(&req); err != nil {
        h.logger.Errorf("[Update] bind error: %v", err)
        otelHelper.Errorf(c, "[Update] bind error: %v", err)
        return
    }
}
```

## 🛠️ 批量迁移脚本

项目提供了自动化迁移脚本:

```bash
cd agent-backend/agent-factory
./scripts/migrate_o11y.sh
```

该脚本会:
1. 查找所有包含 `o11y.Error` 的 Go 文件
2. 自动备份原文件
3. 替换 import 语句
4. 替换函数调用
5. 生成处理报告

## ✅ 验证步骤

迁移完成后,请执行以下验证:

```bash
# 1. 格式化代码
make fmt

# 2. 运行 linter
make ciLint

# 3. 运行测试
make goTest

# 4. 编译检查
go build -o agent-factory ./main.go
```

## 📋 待迁移文件清单

按优先级排序的待迁移文件列表:

### 高优先级 (核心业务逻辑)
- [ ] `src/domain/service/agentrunsvc/chat_process.go`
- [ ] `src/domain/service/agentrunsvc/chat_post_process.go`
- [ ] `src/domain/service/agentrunsvc/resumechat.go`
- [ ] `src/domain/service/agentrunsvc/terminatechat.go`

### 中优先级 (HTTP Handlers)
- [ ] `src/driveradapter/api/httphandler/conversationhandler/delete.go`
- [ ] `src/driveradapter/api/httphandler/conversationhandler/detail.go`
- [ ] `src/driveradapter/api/httphandler/conversationhandler/init.go`
- [ ] `src/driveradapter/api/httphandler/conversationhandler/list.go`
- [ ] `src/driveradapter/api/httphandler/conversationhandler/mark_read.go`
- [ ] `src/driveradapter/api/httphandler/agenthandler/*.go`

### 低优先级 (数据访问层)
- [ ] `src/drivenadapter/dbaccess/**/*.go`
- [ ] `src/drivenadapter/httpaccess/**/*.go`

## 🔧 故障排除

### 编译错误: undefined: otelHelper

**问题:** 导入路径错误
**解决:** 确保导入路径正确:
```go
otelHelper "github.com/kweaver-ai/decision-agent/agent-factory/src/infra/opentelemetry"
```

### 日志未输出

**问题:** Logger 未正确初始化
**解决:** 确保在应用启动时初始化了 Logger:
```go
logger := logs.NewLogger(cfg, otelLogger)
logs.WithLogger(ctx, logger)
```

### Span 链路断开

**问题:** Context 未正确传递
**解决:** 确保 Context 在整个调用链中传递:
```go
newCtx, span := otelTrace.StartInternalSpan(ctx)
defer otelTrace.EndSpan(newCtx, err)
```

## 📚 参考文档

- [OpenTelemetry Go 文档](https://opentelemetry.io/docs/instrumentation/go/)
- [OpenTelemetry Logs API](https://pkg.go.dev/go.opentelemetry.io/otel/log)
- [OpenTelemetry Trace API](https://pkg.go.dev/go.opentelemetry.io/otel/trace)

## 🎯 完成标准

迁移完成的标志:

1. ✅ 所有 `o11y.Error` 调用已替换为 `otelHelper.Error/Errorf`
2. ✅ 所有 `o11y.StartServerSpan` 已替换为 `otelTrace.StartServerSpan`
3. ✅ 所有 `o11y.SetAttributes` 已替换为 `otelTrace.SetAttributes`
4. ✅ 所有 `o11y.EndSpan` 已替换为 `otelTrace.EndSpan`
5. ✅ go.mod 中移除 `kweaver-go-lib` 依赖
6. ✅ 所有测试通过
7. ✅ 代码格式化和 lint 检查通过

## 📞 联系方式

如有问题,请联系:
- 项目负责人: [您的名字]
- 技术支持: [support@example.com]
