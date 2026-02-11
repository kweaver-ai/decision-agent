package observabilitysvc

import (
	"context"
	"testing"

	observabilityreq "github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/observability/req"
	"github.com/stretchr/testify/assert"
)

func TestObservabilitySvc_RunList_PanicsWithoutUniQueryHttp(t *testing.T) {
	svc := &observabilitySvc{}
	// uniQueryHttp is nil

	ctx := context.Background()
	req := &observabilityreq.RunListReq{}

	assert.Panics(t, func() {
		_, _ = svc.RunList(ctx, req)
	})
}

func TestObservabilitySvc_SessionList_PanicsWithoutUniQueryHttp(t *testing.T) {
	svc := &observabilitySvc{}
	// uniQueryHttp is nil

	ctx := context.Background()
	req := &observabilityreq.SessionListReq{}

	assert.Panics(t, func() {
		_, _ = svc.SessionList(ctx, req)
	})
}

func TestObservabilitySvc_SessionDetail_PanicsWithoutUniQueryHttp(t *testing.T) {
	svc := &observabilitySvc{}
	// uniQueryHttp is nil

	ctx := context.Background()
	req := &observabilityreq.SessionDetailReq{}

	assert.Panics(t, func() {
		_, _ = svc.SessionDetail(ctx, req)
	})
}

func TestObservabilitySvc_RunDetail_PanicsWithoutUniQueryHttp(t *testing.T) {
	svc := &observabilitySvc{}
	// uniQueryHttp is nil

	ctx := context.Background()
	req := &observabilityreq.RunDetailReq{}

	assert.Panics(t, func() {
		_, _ = svc.RunDetail(ctx, req)
	})
}

func TestObservabilitySvc_AnalyticsQuery_PanicsWithoutUniQueryHttp(t *testing.T) {
	svc := &observabilitySvc{}
	// uniQueryHttp is nil

	ctx := context.Background()
	req := &observabilityreq.AnalyticsQueryReq{}

	assert.Panics(t, func() {
		_, _ = svc.AnalyticsQuery(ctx, req)
	})
}

