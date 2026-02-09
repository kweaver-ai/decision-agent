package constant

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestLoggerKey(t *testing.T) {
	assert.Equal(t, contextKey("logger"), LoggerKey)
}

func TestMetricsKey(t *testing.T) {
	assert.Equal(t, contextKey("metrics"), MetricsKey)
}

func TestContextKeys_AreUnique(t *testing.T) {
	assert.NotEqual(t, LoggerKey, MetricsKey)
}

func TestContextKeys_NotEmpty(t *testing.T) {
	assert.NotEmpty(t, string(LoggerKey))
	assert.NotEmpty(t, string(MetricsKey))
}

func TestContextKey_String(t *testing.T) {
	key := contextKey("test")
	assert.Equal(t, "test", string(key))
}

func TestContextKey_InContext(t *testing.T) {
	ctx := context.WithValue(context.Background(), LoggerKey, "logger_value")

	value := ctx.Value(LoggerKey)
	assert.NotNil(t, value)
	assert.Equal(t, "logger_value", value)
}
