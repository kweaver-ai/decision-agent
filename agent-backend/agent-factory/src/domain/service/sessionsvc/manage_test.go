package sessionsvc

import (
	"context"
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/session/sessionreq"
	"github.com/stretchr/testify/assert"
)

func TestManage_UnsupportedAction(t *testing.T) {
	svc := &sessionSvc{}

	req := sessionreq.ManageReq{
		Action: "unsupported_action",
	}

	resp, err := svc.Manage(context.Background(), req, nil)

	assert.Error(t, err)
	assert.Contains(t, err.Error(), "unsupported action")
	assert.Empty(t, resp.ConversationSessionID)
}

func TestManage_ValidActionsWithoutDeps(t *testing.T) {
	// Test that valid actions are properly routed
	// Even though they will fail due to missing dependencies,
	// this verifies the routing logic works correctly
	svc := &sessionSvc{}

	testCases := []struct {
		name   string
		action sessionreq.SessionManageActionType
	}{
		{
			name:   "GetInfoOrCreate action",
			action: sessionreq.SessionManageActionGetInfoOrCreate,
		},
		{
			name:   "RecoverLifetimeOrCreate action",
			action: sessionreq.SessionManageActionRecoverLifetimeOrCreate,
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			req := sessionreq.ManageReq{
				Action:         tc.action,
				ConversationID: "conv-123",
				AgentID:        "agent-123",
				AgentVersion:   "v1.0.0",
			}

			// Since HandleGetInfoOrCreate and HandleRecoverLifetimeOrCreate
			// require sessionRedisAcc to be set up, and we're testing without it,
			// these will cause a panic or error.
			// We catch the panic to verify the routing works.
			assert.Panics(t, func() {
				_, _ = svc.Manage(context.Background(), req, nil)
			})
		})
	}
}

func TestTriggerAgentCacheUpsert_NoAgentExecutor(t *testing.T) {
	svc := &sessionSvc{
		// agentExecutorV1 is nil
	}

	req := sessionreq.ManageReq{
		AgentID:      "agent-123",
		AgentVersion: "v1.0.0",
	}

	// This should panic because agentExecutorV1 is nil
	assert.Panics(t, func() {
		_ = svc.triggerAgentCacheUpsert(context.Background(), req, nil)
	})
}
