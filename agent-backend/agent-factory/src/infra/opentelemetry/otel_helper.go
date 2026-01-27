package opentelemetry

import (
	"context"
	"fmt"

	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/codes"
	"go.opentelemetry.io/otel/trace"

	"github.com/kweaver-ai/TelemetrySDK-Go/span/v2/field"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/opentelemetry/logs"
	otelTrace "github.com/kweaver-ai/decision-agent/agent-factory/src/infra/opentelemetry/trace"
)

// Error 记录错误日志并设置 span 状态
// 替代 o11y.Error(ctx, msg)
func Error(ctx context.Context, msg string, attrs ...attribute.KeyValue) {
	// 记录错误日志
	logger := logs.LoggerFromContext(ctx)
	logger.Error(ctx, msg, attrs...)

	// 如果存在 span,设置错误状态
	span := trace.SpanFromContext(ctx)
	if span != nil {
		span.RecordError(fmt.Errorf("%s", msg))
		span.SetStatus(codes.Error, msg)
	}
}

// Errorf 记录格式化的错误日志
// 替代 o11y.Error(ctx, fmt.Sprintf(...))
func Errorf(ctx context.Context, format string, args ...interface{}) {
	msg := fmt.Sprintf(format, args...)
	Error(ctx, msg)
}

// Info 记录信息日志
// 替代 o11y.Info(ctx, msg)
func Info(ctx context.Context, msg string, attrs ...attribute.KeyValue) {
	logger := logs.LoggerFromContext(ctx)
	logger.Info(ctx, msg, attrs...)
}

// Infof 记录格式化的信息日志
func Infof(ctx context.Context, format string, args ...interface{}) {
	msg := fmt.Sprintf(format, args...)
	Info(ctx, msg)
}

// Warn 记录警告日志
// 替代 o11y.Warn(ctx, msg)
func Warn(ctx context.Context, msg string, attrs ...attribute.KeyValue) {
	logger := logs.LoggerFromContext(ctx)
	logger.Warn(ctx, msg, attrs...)
}

// Warnf 记录格式化的警告日志
func Warnf(ctx context.Context, format string, args ...interface{}) {
	msg := fmt.Sprintf(format, args...)
	Warn(ctx, msg)
}

// Debug 记录调试日志
// 替代 o11y.Debug(ctx, msg)
func Debug(ctx context.Context, msg string, attrs ...attribute.KeyValue) {
	logger := logs.LoggerFromContext(ctx)
	logger.Debug(ctx, msg, attrs...)
}

// Debugf 记录格式化的调试日志
func Debugf(ctx context.Context, format string, args ...interface{}) {
	msg := fmt.Sprintf(format, args...)
	Debug(ctx, msg)
}

// LogWithError 记录错误日志并返回 error
// 用于需要返回错误的场景
func LogWithError(ctx context.Context, msg string, err error) error {
	attrs := []attribute.KeyValue{
		attribute.String("error", err.Error()),
	}
	Error(ctx, msg, attrs...)
	return err
}

// StartSpan 创建内部 span
// 替代 o11y.StartSpan,但推荐使用 otelTrace.StartInternalSpan
func StartSpan(ctx context.Context, name string) (context.Context, trace.Span) {
	newCtx, span := otelTrace.StartInternalSpan(ctx)
	return newCtx, span
}

// SetAttributes 设置 span 属性
// 替代 o11y.SetAttributes
func SetAttributes(ctx context.Context, attrs ...attribute.KeyValue) {
	otelTrace.SetAttributes(ctx, attrs...)
}

// EndSpan 结束 span
// 替代 o11y.EndSpan
func EndSpan(ctx context.Context, err error) {
	otelTrace.EndSpan(ctx, err)
}

// InfoWithAttr 使用 TelemetrySDK 的 field.LogOptionFunc 记录日志
// 这是一个临时兼容函数，用于保持与 TelemetrySDK 的兼容性
// TODO: 逐步迁移到纯 OpenTelemetry 的日志记录方式
func InfoWithAttr(ctx context.Context, msg string, options ...field.LogOptionFunc) {
	// 由于 field.LogOptionFunc 是 TelemetrySDK 的特定类型
	// 与 OpenTelemetry 不兼容，这里暂时不做任何操作
	// 未来可以考虑将 field 属性转换为 OpenTelemetry 属性
	_ = msg
	_ = options
}
