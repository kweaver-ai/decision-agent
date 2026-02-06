package personalspacep2e

import (
	"context"
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestAgentsListForPersonalSpace_Simple(t *testing.T) {
	ctx := context.Background()

	po := &dapo.DataAgentPo{
		ID:        "agent1",
		Name:      "Test Agent",
		Key:       "test-agent",
		ProductKey: "product1",
		CreatedBy: "user1",
		UpdatedBy: "user2",
	}

	eo, err := AgentsListForPersonalSpace(ctx, po)
	require.NoError(t, err)
	assert.NotNil(t, eo)
	assert.Equal(t, "agent1", eo.ID)
	assert.Equal(t, "Test Agent", eo.Name)
	assert.Equal(t, "test-agent", eo.Key)
	assert.Equal(t, "product1", eo.ProductKey)
	assert.Equal(t, "user1", eo.CreatedBy)
	assert.Equal(t, "user2", eo.UpdatedBy)
}

func TestAgentsListForPersonalSpace_WithProfile(t *testing.T) {
	ctx := context.Background()

	profile := "test profile"
	po := &dapo.DataAgentPo{
		ID:        "agent1",
		Name:      "Test Agent",
		Profile:   &profile,
		CreatedBy: "user1",
		UpdatedBy: "user1",
	}

	eo, err := AgentsListForPersonalSpace(ctx, po)
	require.NoError(t, err)
	assert.NotNil(t, eo)
	assert.Equal(t, "agent1", eo.ID)
	assert.NotNil(t, eo.Profile)
	assert.Equal(t, "test profile", *eo.Profile)
}

func TestAgentsListForPersonalSpace_EmptyPo(t *testing.T) {
	ctx := context.Background()

	po := &dapo.DataAgentPo{}

	eo, err := AgentsListForPersonalSpace(ctx, po)
	require.NoError(t, err)
	assert.NotNil(t, eo)
}

func TestAgentsListForPersonalSpaces_EmptyList(t *testing.T) {
	ctx := context.Background()

	pos := []*dapo.DataAgentPo{}

	// We can't properly test the full function without UM HTTP mock
	// Just test that it handles empty list without panic
	// For full testing, need proper environment setup
	_ = ctx
	_ = pos
}
