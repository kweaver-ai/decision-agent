package publishedsvc

import (
	"context"
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/published/pubedreq"
	"github.com/stretchr/testify/assert"
)

func TestPublishedSvc_GetPublishedAgentList_PanicsWithoutPmsAgentPos(t *testing.T) {
	svc := &publishedSvc{}
	// All repos are nil

	ctx := context.Background()
	req := &pubedreq.PubedAgentListReq{
		Size: 10,
	}

	assert.Panics(t, func() {
		_, _ = svc.GetPublishedAgentList(ctx, req)
	})
}
