package dapo

import (
	"testing"
)

func TestSpacePo_TableName(t *testing.T) {
	t.Parallel()

	t.Run("table name", func(t *testing.T) {
		t.Parallel()

		po := &SpacePo{}
		tableName := po.TableName()

		expected := "t_custom_space"
		if tableName != expected {
			t.Errorf("Expected table name to be '%s', got '%s'", expected, tableName)
		}
	})
}

func TestSpacePo(t *testing.T) {
	t.Parallel()

	t.Run("create space PO", func(t *testing.T) {
		t.Parallel()

		po := &SpacePo{
			ID:        "space-123",
			Name:      "Test Space",
			Key:       "test-space",
			Profile:   "Test profile",
			CreatedBy: "user-1",
			CreatedAt: 1234567890,
			UpdatedBy: "user-1",
			UpdatedAt: 1234567890,
		}

		if po.ID != "space-123" {
			t.Errorf("Expected ID to be 'space-123', got '%s'", po.ID)
		}

		if po.Name != "Test Space" {
			t.Errorf("Expected Name to be 'Test Space', got '%s'", po.Name)
		}

		if po.Key != "test-space" {
			t.Errorf("Expected Key to be 'test-space', got '%s'", po.Key)
		}

		if po.Profile != "Test profile" {
			t.Errorf("Expected Profile to be 'Test profile', got '%s'", po.Profile)
		}

		if po.CreatedBy != "user-1" {
			t.Errorf("Expected CreatedBy to be 'user-1', got '%s'", po.CreatedBy)
		}

		if po.CreatedAt != 1234567890 {
			t.Errorf("Expected CreatedAt to be 1234567890, got %d", po.CreatedAt)
		}

		if po.UpdatedBy != "user-1" {
			t.Errorf("Expected UpdatedBy to be 'user-1', got '%s'", po.UpdatedBy)
		}

		if po.UpdatedAt != 1234567890 {
			t.Errorf("Expected UpdatedAt to be 1234567890, got %d", po.UpdatedAt)
		}
	})

	t.Run("space with deletion info", func(t *testing.T) {
		t.Parallel()

		po := &SpacePo{
			ID:        "space-456",
			DeletedBy: "user-2",
			DeletedAt: 9999999999,
		}

		if po.ID != "space-456" {
			t.Errorf("Expected ID to be 'space-456', got '%s'", po.ID)
		}

		if po.DeletedBy != "user-2" {
			t.Errorf("Expected DeletedBy to be 'user-2', got '%s'", po.DeletedBy)
		}

		if po.DeletedAt != 9999999999 {
			t.Errorf("Expected DeletedAt to be 9999999999, got %d", po.DeletedAt)
		}
	})
}
