# OpenTelemetry 迁移快速参考

## 🎯 核心概念

**目标**: 将 `kweaver-go-lib/observability` (o11y) 替换为开源 OpenTelemetry SDK

**关键优势**:
- ✅ 开源标准,社区支持
- ✅ 与云厂商无关
- ✅ 功能更强大
- ✅ 更好的可维护性

## 📦 新增文件

```
src/infra/opentelemetry/
├── logs/
│   └── logger.go          # OpenTelemetry Logger 实现
├── trace/
│   └── trace.go           # OpenTelemetry Trace 实现
└── otel_helper.go         # 辅助工具函数 ⭐
```

## 🔁 API 快速映射

### 日志记录

```go
// 旧方式
o11y.Error(ctx, fmt.Sprintf("[Update] failed: %v", err))
o11y.Info(ctx, "Operation completed")
o11y.Warn(ctx, "Deprecated API used")

// 新方式 ⭐
otelHelper.Errorf(ctx, "[Update] failed: %v", err)
otelHelper.Info(ctx, "Operation completed")
otelHelper.Warn(ctx, "Deprecated API used")
```

### 追踪

```go
// 旧方式
newCtx, span := o11y.StartServerSpan(c)
o11y.SetAttributes(newCtx, attrs)
o11y.EndSpan(newCtx, err)

// 新方式 ⭐
newCtx, span := otelTrace.StartServerSpan(c)
otelTrace.SetAttributes(newCtx, attrs)
otelTrace.EndSpan(newCtx, err)
```

### 内部 Span

```go
// 新方式 (推荐)
newCtx, span := otelTrace.StartInternalSpan(ctx)
defer otelTrace.EndSpan(newCtx, err)
```

## 📝 迁移步骤

### 单个文件迁移

```bash
# 1. 打开文件
vim src/path/to/file.go

# 2. 替换 import
# 删除: o11y "github.com/kweaver-ai/kweaver-go-lib/observability"
# 添加: otelHelper "github.com/kweaver-ai/decision-agent/agent-factory/src/infra/opentelemetry"

# 3. 替换函数调用
# o11y.Error(ctx, fmt.Sprintf(...)) → otelHelper.Errorf(ctx, ...)
# o11y.Error(ctx, "...") → otelHelper.Error(ctx, "...")

# 4. 保存退出
:wq

# 5. 格式化代码
make fmt
```

### 批量迁移

```bash
cd agent-backend/agent-factory
./scripts/migrate_o11y.sh
```

## ✅ 验证清单

- [ ] 代码编译通过: `go build`
- [ ] 格式化检查: `make fmt`
- [ ] Lint 检查: `make ciLint`
- [ ] 测试通过: `make goTest`
- [ ] 日志正常输出
- [ ] 追踪链路完整

## 🆘 常见问题

### Q: 编译错误: undefined: otelHelper
**A:** 检查 import 路径是否正确:
```go
import (
    otelHelper "github.com/kweaver-ai/decision-agent/agent-factory/src/infra/opentelemetry"
)
```

### Q: 日志未输出
**A:** 确保 Logger 已初始化并注入到 context:
```go
logger := logs.NewLogger(cfg, otelLogger)
ctx = logs.WithLogger(ctx, logger)
```

### Q: Trace 链路断开
**A:** 确保 Context 正确传递:
```go
newCtx, span := otelTrace.StartInternalSpan(ctx)
defer otelTrace.EndSpan(newCtx, err)
```

## 📊 迁移进度

- ✅ 基础设施: 100% (Logger, Trace, Helper)
- ✅ 核心文件: 3 个 (中间件, chat.go, 示例 handler)
- ⏳ 待迁移: ~98 个文件
- 📈 总进度: ~3%

## 📚 详细文档

- **完整指南**: `O11Y_MIGRATION_GUIDE.md`
- **迁移总结**: `MIGRATION_SUMMARY.md`
- **脚本工具**: `scripts/migrate_o11y.sh`

## 🚀 快速开始

```bash
# 1. 查看迁移指南
cat O11Y_MIGRATION_GUIDE.md

# 2. 运行批量迁移 (可选)
cd agent-backend/agent-factory
./scripts/migrate_o11y.sh

# 3. 验证
make fmt && make ciLint && make goTest
```

---

**提示**: 所有示例代码已准备就绪,只需复制粘贴即可! 🎉
