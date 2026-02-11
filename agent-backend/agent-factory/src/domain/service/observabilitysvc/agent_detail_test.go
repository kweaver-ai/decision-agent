package observabilitysvc

import (
	"context"
	"testing"

	observabilityreq "github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/observability/req"
	"github.com/stretchr/testify/assert"
)

func TestObservabilitySvc_AgentDetail_PanicsWithoutAgentFactory(t *testing.T) {
	svc := &observabilitySvc{}
	// All dependencies are nil

	ctx := context.Background()
	req := &observabilityreq.AgentDetailReq{
		AgentID: "agent-123",
	}

	assert.Panics(t, func() {
		_, _ = svc.AgentDetail(ctx, req)
	})
}
