package dapo

import (
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/enum/cdaenum"
)

func TestSpaceResourcePo_TableName(t *testing.T) {
	t.Run("table name", func(t *testing.T) {
		po := &SpaceResourcePo{}
		tableName := po.TableName()

		expected := "t_custom_space_resource"
		if tableName != expected {
			t.Errorf("Expected table name to be '%s', got '%s'", expected, tableName)
		}
	})
}

func TestSpaceResourcePo(t *testing.T) {
	t.Run("create space resource PO", func(t *testing.T) {
		po := &SpaceResourcePo{
			ID:           123,
			SpaceID:      "space-123",
			SpaceKey:     "test-space",
			ResourceType: cdaenum.ResourceTypeDataAgent,
			ResourceID:   "agent-123",
			CreatedBy:    "creator-1",
			CreatedAt:    1234567890,
		}

		if po.ID != 123 {
			t.Errorf("Expected ID to be 123, got %d", po.ID)
		}
		if po.SpaceID != "space-123" {
			t.Errorf("Expected SpaceID to be 'space-123', got '%s'", po.SpaceID)
		}
		if po.SpaceKey != "test-space" {
			t.Errorf("Expected SpaceKey to be 'test-space', got '%s'", po.SpaceKey)
		}
		if po.ResourceType != cdaenum.ResourceTypeDataAgent {
			t.Errorf("Expected ResourceType to be DataAgent, got %v", po.ResourceType)
		}
		if po.ResourceID != "agent-123" {
			t.Errorf("Expected ResourceID to be 'agent-123', got '%s'", po.ResourceID)
		}
		if po.CreatedBy != "creator-1" {
			t.Errorf("Expected CreatedBy to be 'creator-1', got '%s'", po.CreatedBy)
		}
		if po.CreatedAt != 1234567890 {
			t.Errorf("Expected CreatedAt to be 1234567890, got %d", po.CreatedAt)
		}
	})

	t.Run("space resource with agent template type", func(t *testing.T) {
		po := &SpaceResourcePo{
			ID:           456,
			SpaceID:      "space-456",
			SpaceKey:     "test-space-2",
			ResourceType: cdaenum.ResourceTypeDataAgentTpl,
			ResourceID:   "template-456",
			CreatedBy:    "creator-2",
			CreatedAt:    1234567890,
		}

		if po.ResourceType != cdaenum.ResourceTypeDataAgentTpl {
			t.Errorf("Expected ResourceType to be DataAgentTpl, got %v", po.ResourceType)
		}
	})
}
