package v3agentconfigsvc

import (
	"context"
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/service"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/agent_config/agentconfigreq"
	"github.com/stretchr/testify/assert"
)

func TestDataAgentConfigSvc_Copy2Tpl_PanicsWithoutAgentConfRepo(t *testing.T) {
	svc := &dataAgentConfigSvc{
		SvcBase: service.NewSvcBase(),
	}

	ctx := context.Background()
	agentID := "agent-123"
	req := &agentconfigreq.Copy2TplReq{}

	assert.Panics(t, func() {
		_, _, _ = svc.Copy2Tpl(ctx, agentID, req, nil)
	})
}
