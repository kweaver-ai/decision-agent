package spacevo

import (
	"github.com/stretchr/testify/assert"
	"testing"
)

func TestResourceUniq(t *testing.T) {
	tests := []struct {
		name     string
		resource *ResourceUniq
	}{
		{
			name: "数据代理",
			resource: &ResourceUniq{
				ResourceType: "data_agent",
				ResourceID:   "agent-123",
			},
		},
		{
			name: "其他类型",
			resource: &ResourceUniq{
				ResourceType: "other",
				ResourceID:   "resource-456",
			},
		},
		{
			name: "空值",
			resource: &ResourceUniq{
				ResourceType: "",
				ResourceID:   "",
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			assert.Equal(t, tt.resource.ResourceType, tt.resource.ResourceType)
			assert.Equal(t, tt.resource.ResourceID, tt.resource.ResourceID)
		})
	}
}

func TestResourceAssoc(t *testing.T) {
	tests := []struct {
		name   string
		assoc  ResourceAssoc
		wantID int64
	}{
		{
			name: "有效关联ID",
			assoc: ResourceAssoc{
				ResourceUniq: ResourceUniq{
					ResourceType: "data_agent",
					ResourceID:   "agent-123",
				},
				AssocID: 67890,
			},
			wantID: 67890,
		},
		{
			name: "零ID",
			assoc: ResourceAssoc{
				ResourceUniq: ResourceUniq{
					ResourceType: "role",
					ResourceID:   "role-456",
				},
				AssocID: 0,
			},
			wantID: 0,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			assert.Equal(t, tt.wantID, tt.assoc.AssocID)
		})
	}
}
