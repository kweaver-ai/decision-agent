package conversationsvc

import (
	"context"
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/service"
	"github.com/stretchr/testify/assert"
)

func TestConversationSvc_Delete_PanicsWithoutConversationRepo(t *testing.T) {
	svc := &conversationSvc{
		SvcBase: service.NewSvcBase(),
		// conversationRepo is nil
	}

	ctx := context.Background()
	conversationID := "conv-123"

	// This will panic because conversationRepo is nil
	assert.Panics(t, func() {
		_ = svc.Delete(ctx, conversationID)
	})
}

