package dapo

import (
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cenum"
)

func TestSpaceMemberPo_TableName(t *testing.T) {
	t.Run("table name", func(t *testing.T) {
		po := &SpaceMemberPo{}
		tableName := po.TableName()

		expected := "t_custom_space_member"
		if tableName != expected {
			t.Errorf("Expected table name to be '%s', got '%s'", expected, tableName)
		}
	})
}

func TestSpaceMemberPo(t *testing.T) {
	t.Run("create space member PO", func(t *testing.T) {
		po := &SpaceMemberPo{
			ID:       123,
			SpaceID:  "space-123",
			SpaceKey: "test-space",
			ObjType:  cenum.OrgObjTypeUser,
			ObjID:    "user-123",
			CreatedBy: "creator-1",
			CreatedAt: 1234567890,
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
		if po.ObjType != cenum.OrgObjTypeUser {
			t.Errorf("Expected ObjType to be User, got %v", po.ObjType)
		}
		if po.ObjID != "user-123" {
			t.Errorf("Expected ObjID to be 'user-123', got '%s'", po.ObjID)
		}
		if po.CreatedBy != "creator-1" {
			t.Errorf("Expected CreatedBy to be 'creator-1', got '%s'", po.CreatedBy)
		}
		if po.CreatedAt != 1234567890 {
			t.Errorf("Expected CreatedAt to be 1234567890, got %d", po.CreatedAt)
		}
	})

	t.Run("space member with dept type", func(t *testing.T) {
		po := &SpaceMemberPo{
			ID:       456,
			SpaceID:  "space-456",
			ObjType:  cenum.OrgObjTypeDep,
			ObjID:    "dept-456",
			CreatedBy: "creator-2",
			CreatedAt: 1234567890,
		}

		if po.ObjType != cenum.OrgObjTypeDep {
			t.Errorf("Expected ObjType to be Dept, got %v", po.ObjType)
		}
	})

	t.Run("space member with user group type", func(t *testing.T) {
		po := &SpaceMemberPo{
			ID:       789,
			SpaceID:  "space-789",
			ObjType:  cenum.OrgObjTypeGroup,
			ObjID:    "group-789",
			CreatedBy: "creator-3",
			CreatedAt: 1234567890,
		}

		if po.ObjType != cenum.OrgObjTypeGroup {
			t.Errorf("Expected ObjType to be Group, got %v", po.ObjType)
		}
	})
}
