package sessionsvc

import (
	"context"
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/session/sessionreq"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/ctype"
	"github.com/stretchr/testify/assert"
)

func TestHandleGetInfoOrCreate(t *testing.T) {
	t.Run("nil service causes panic", func(t *testing.T) {
		var svc *sessionSvc
		ctx := context.Background()
		req := sessionreq.ManageReq{
			ConversationID: "conv-123",
		}
		visitorInfo := &ctype.VisitorInfo{}

		// This will panic when trying to use sessionRedisAcc
		assert.Panics(t, func() {
			svc.HandleGetInfoOrCreate(ctx, req, visitorInfo, false)
		})
	})

	t.Run("nil session redis causes panic", func(t *testing.T) {
		svc := &sessionSvc{
			// sessionRedisAcc is nil, will panic
		}
		ctx := context.Background()
		req := sessionreq.ManageReq{
			ConversationID: "conv-123",
		}
		visitorInfo := &ctype.VisitorInfo{}

		// This will panic when trying to use sessionRedisAcc
		assert.Panics(t, func() {
			svc.HandleGetInfoOrCreate(ctx, req, visitorInfo, false)
		})
	})
}

