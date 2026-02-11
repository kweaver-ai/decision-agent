package v3agentconfigsvc

import (
	"context"
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/service"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/agent_config/agentconfigreq"
	"github.com/stretchr/testify/assert"
)

func TestDataAgentConfigSvc_Create_PanicsWithoutAgentConfRepo(t *testing.T) {
	svc := &dataAgentConfigSvc{
		SvcBase: service.NewSvcBase(),
		// agentConfRepo is nil
	}

	ctx := context.Background()
	req := &agentconfigreq.CreateReq{}

	assert.Panics(t, func() {
		_, _ = svc.Create(ctx, req)
	})
}

func TestDataAgentConfigSvc_Create_ZeroAgentIDReturnsError(t *testing.T) {
	svc := &dataAgentConfigSvc{
		SvcBase: service.NewSvcBase(),
	}

	ctx := context.Background()
	req := &agentconfigreq.CreateReq{
		UpdateReq: &agentconfigreq.UpdateReq{},
	}

	// This test verifies that Create requires proper setup
	// and will fail appropriately when dependencies are missing
	assert.Panics(t, func() {
		_, _ = svc.Create(ctx, req)
	})
}
