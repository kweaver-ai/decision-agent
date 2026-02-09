package chelper

import (
	"context"
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cenum"
	"github.com/stretchr/testify/assert"
)

func TestIsInternalAPIFromCtx_WithTrueValue(t *testing.T) {
	ctx := context.WithValue(context.Background(), cenum.InternalAPIFlagCtxKey.String(), true)

	isInternal := IsInternalAPIFromCtx(ctx)

	assert.True(t, isInternal)
}

func TestIsInternalAPIFromCtx_WithFalseValue(t *testing.T) {
	ctx := context.WithValue(context.Background(), cenum.InternalAPIFlagCtxKey.String(), false)

	isInternal := IsInternalAPIFromCtx(ctx)

	assert.False(t, isInternal)
}

func TestIsInternalAPIFromCtx_WithNilValue(t *testing.T) {
	ctx := context.Background()

	isInternal := IsInternalAPIFromCtx(ctx)

	assert.False(t, isInternal)
}

func TestIsInternalAPIFromCtx_WithInvalidType(t *testing.T) {
	ctx := context.WithValue(context.Background(), cenum.InternalAPIFlagCtxKey.String(), "not_a_bool")

	assert.Panics(t, func() {
		IsInternalAPIFromCtx(ctx)
	})
}

func TestIsInternalAPIFromCtx_WithIntValue(t *testing.T) {
	ctx := context.WithValue(context.Background(), cenum.InternalAPIFlagCtxKey.String(), 1)

	assert.Panics(t, func() {
		IsInternalAPIFromCtx(ctx)
	})
}

func TestIsInternalAPIFromCtx_DerivedContext(t *testing.T) {
	baseCtx := context.Background()
	ctx := context.WithValue(baseCtx, cenum.InternalAPIFlagCtxKey.String(), true)

	isInternal := IsInternalAPIFromCtx(ctx)

	assert.True(t, isInternal)
}
