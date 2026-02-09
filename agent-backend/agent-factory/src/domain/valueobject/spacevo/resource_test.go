package spacevo

import (
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/enum/cdaenum"
	"github.com/stretchr/testify/assert"
)

func TestResourceUniq_New(t *testing.T) {
	resource := &ResourceUniq{
		ResourceType: cdaenum.ResourceTypeDataAgent,
		ResourceID:   "resource-123",
	}

	assert.NotNil(t, resource)
	assert.Equal(t, cdaenum.ResourceTypeDataAgent, resource.ResourceType)
	assert.Equal(t, "resource-123", resource.ResourceID)
}

func TestResourceUniq_EmptyFields(t *testing.T) {
	resource := &ResourceUniq{}

	assert.NotNil(t, resource)
	assert.Empty(t, resource.ResourceID)
}

func TestResourceAssoc_New(t *testing.T) {
	assoc := &ResourceAssoc{
		ResourceUniq: ResourceUniq{
			ResourceType: cdaenum.ResourceTypeDataAgent,
			ResourceID:   "resource-456",
		},
		AssocID: 2002,
	}

	assert.NotNil(t, assoc)
	assert.Equal(t, cdaenum.ResourceTypeDataAgent, assoc.ResourceType)
	assert.Equal(t, "resource-456", assoc.ResourceID)
	assert.Equal(t, int64(2002), assoc.AssocID)
}

func TestResourceAssoc_EmptyFields(t *testing.T) {
	assoc := &ResourceAssoc{}

	assert.NotNil(t, assoc)
	assert.Empty(t, assoc.ResourceID)
	assert.Equal(t, int64(0), assoc.AssocID)
}

func TestResourceAssoc_WithLargeAssocID(t *testing.T) {
	assoc := &ResourceAssoc{
		ResourceUniq: ResourceUniq{
			ResourceType: cdaenum.ResourceTypeDataAgent,
			ResourceID:   "resource-789",
		},
		AssocID: 9223372036854775807,
	}

	assert.Equal(t, int64(9223372036854775807), assoc.AssocID)
}
