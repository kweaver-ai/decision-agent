package spaceeo

import (
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/valueobject/agentvo"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	"github.com/stretchr/testify/assert"
)

func TestNewSpaceResource_CreatesNewInstance(t *testing.T) {
	t.Parallel()

	resource1 := NewSpaceResource()
	resource2 := NewSpaceResource()

	assert.NotNil(t, resource1)
	assert.NotNil(t, resource2)
	// Both have PublishedAgentInfo
	assert.NotNil(t, resource1.PublishedAgentInfo)
	assert.NotNil(t, resource2.PublishedAgentInfo)
}

func TestSpaceResource_Fields(t *testing.T) {
	t.Parallel()

	resource := &SpaceResource{
		SpaceResourcePo: dapo.SpaceResourcePo{
			ID: 123,
		},
		ResourceName: "Test Resource",
	}

	assert.Equal(t, int64(123), resource.ID)
	assert.Equal(t, "Test Resource", resource.ResourceName)
}

func TestSpaceResource_WithPublishedAgentInfo(t *testing.T) {
	t.Parallel()

	resource := &SpaceResource{
		PublishedAgentInfo: agentvo.NewPublishedAgentInfo(),
	}

	assert.NotNil(t, resource.PublishedAgentInfo)
}
