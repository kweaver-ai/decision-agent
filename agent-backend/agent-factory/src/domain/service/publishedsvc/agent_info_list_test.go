package publishedsvc

import (
	"context"
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/published/pubedreq"
	"github.com/stretchr/testify/assert"
)

func TestPublishedSvc_GetPubedAgentInfoList_PanicsWithoutPubedAgentRepo(t *testing.T) {
	svc := &publishedSvc{}
	// pubedAgentRepo is nil

	ctx := context.Background()
	req := &pubedreq.PAInfoListReq{
		AgentKeys: []string{"agent-123"},
	}

	assert.Panics(t, func() {
		_, _ = svc.GetPubedAgentInfoList(ctx, req)
	})
}

func TestPublishedSvc_GetPubedAgentInfoList_EmptyAgentKeys(t *testing.T) {
	svc := &publishedSvc{}

	ctx := context.Background()
	req := &pubedreq.PAInfoListReq{
		AgentKeys: []string{},
	}

	// This should panic when trying to call the repo
	assert.Panics(t, func() {
		_, _ = svc.GetPubedAgentInfoList(ctx, req)
	})
}

func TestPublishedSvc_GetPubedAgentInfoList_SingleAgentKey(t *testing.T) {
	svc := &publishedSvc{}

	ctx := context.Background()
	req := &pubedreq.PAInfoListReq{
		AgentKeys: []string{"agent-123", "agent-456"},
	}

	// This should not panic even though repo is not set
	// It will panic when trying to call the repo
	assert.Panics(t, func() {
		_, _ = svc.GetPubedAgentInfoList(ctx, req)
	})
}

func TestPublishedSvc_GetPubedAgentInfoList_WithNeedConfigFields(t *testing.T) {
	svc := &publishedSvc{}

	ctx := context.Background()
	req := &pubedreq.PAInfoListReq{
		AgentKeys:       []string{"agent-123"},
		NeedConfigFields: []string{"name", "profile"},
	}

	// This should panic when trying to call the repo
	assert.Panics(t, func() {
		_, _ = svc.GetPubedAgentInfoList(ctx, req)
	})
}
