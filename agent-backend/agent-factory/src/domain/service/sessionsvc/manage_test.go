package sessionsvc

import (
	"context"
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/session/sessionreq"
	"github.com/stretchr/testify/assert"
)

func TestTriggerAgentCacheUpsert(t *testing.T) {
	t.Run("nil agent executor causes panic", func(t *testing.T) {
		svc := &sessionSvc{
			// agentExecutorV1 is nil, will panic
		}
		ctx := context.Background()
		req := sessionreq.ManageReq{}

		// This should panic because agentExecutorV1 is nil
		assert.Panics(t, func() {
			_ = svc.triggerAgentCacheUpsert(ctx, req, nil)
		})
	})
}

