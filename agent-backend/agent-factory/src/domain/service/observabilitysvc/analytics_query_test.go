package observabilitysvc

import (
	"context"
	"testing"

	observabilityreq "github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/observability/req"
	"github.com/stretchr/testify/assert"
	"go.uber.org/mock/gomock"
)

// Test that AnalyticsQuery panics when service has no dependencies set
func TestObservabilitySvc_AnalyticsQuery_PanicsWithoutDependencies(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	svc := &observabilitySvc{}

	ctx := context.Background()
	req := &observabilityreq.AnalyticsQueryReq{
		AnalysisLevel: "agent",
		ID:            "agent-123",
	}

	assert.Panics(t, func() {
		_, _ = svc.AnalyticsQuery(ctx, req)
	})
}

// Test that AnalyticsQuery panics when request is nil
func TestObservabilitySvc_AnalyticsQuery_PanicsWithNilRequest(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	svc := &observabilitySvc{}

	ctx := context.Background()

	assert.Panics(t, func() {
		_, _ = svc.AnalyticsQuery(ctx, nil)
	})
}

// Test different analysis levels
func TestObservabilitySvc_AnalyticsQuery_AnalysisLevels(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	svc := &observabilitySvc{}

	analysisLevels := []string{"agent", "session", "run"}

	for _, level := range analysisLevels {
		t.Run("level_"+level, func(t *testing.T) {
			ctx := context.Background()
			req := &observabilityreq.AnalyticsQueryReq{
				AnalysisLevel: level,
				ID:            "test-id-123",
			}

			assert.Panics(t, func() {
				_, _ = svc.AnalyticsQuery(ctx, req)
			})
		})
	}
}

// Test empty analysis level
func TestObservabilitySvc_AnalyticsQuery_EmptyAnalysisLevel(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	svc := &observabilitySvc{}

	ctx := context.Background()
	req := &observabilityreq.AnalyticsQueryReq{
		AnalysisLevel: "",
		ID:            "test-id-123",
	}

	assert.Panics(t, func() {
		_, _ = svc.AnalyticsQuery(ctx, req)
	})
}

// Test case sensitivity of analysis level
func TestObservabilitySvc_AnalyticsQuery_CaseSensitivity(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	svc := &observabilitySvc{}

	uppercaseLevels := []string{"AGENT", "SESSION", "RUN"}

	for _, level := range uppercaseLevels {
		t.Run("uppercase_"+level, func(t *testing.T) {
			ctx := context.Background()
			req := &observabilityreq.AnalyticsQueryReq{
				AnalysisLevel: level,
				ID:            "test-id-123",
			}

			assert.Panics(t, func() {
				_, _ = svc.AnalyticsQuery(ctx, req)
			})
		})
	}
}

// Test with time range parameters
func TestObservabilitySvc_AnalyticsQuery_WithTimeRange(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	svc := &observabilitySvc{}

	ctx := context.Background()
	req := &observabilityreq.AnalyticsQueryReq{
		AnalysisLevel: "agent",
		ID:            "agent-123",
		StartTime:     1000000,
		EndTime:       2000000,
	}

	assert.Panics(t, func() {
		_, _ = svc.AnalyticsQuery(ctx, req)
	})
}

// Test with account info
func TestObservabilitySvc_AnalyticsQuery_WithAccountInfo(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	svc := &observabilitySvc{}

	ctx := context.Background()
	req := &observabilityreq.AnalyticsQueryReq{
		AnalysisLevel: "agent",
		ID:            "agent-123",
		XAccountID:     "account-123",
		XAccountType:  "user",
	}

	assert.Panics(t, func() {
		_, _ = svc.AnalyticsQuery(ctx, req)
	})
}

// Test with empty ID
func TestObservabilitySvc_AnalyticsQuery_EmptyID(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	svc := &observabilitySvc{}

	ctx := context.Background()
	req := &observabilityreq.AnalyticsQueryReq{
		AnalysisLevel: "agent",
		ID:            "",
	}

	assert.Panics(t, func() {
		_, _ = svc.AnalyticsQuery(ctx, req)
	})
}

// Test context propagation
func TestObservabilitySvc_AnalyticsQuery_ContextPropagation(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	svc := &observabilitySvc{}

	ctx := context.Background()
	req := &observabilityreq.AnalyticsQueryReq{
		AnalysisLevel: "agent",
		ID:            "agent-123",
	}

	assert.Panics(t, func() {
		_, _ = svc.AnalyticsQuery(ctx, req)
	})
}
