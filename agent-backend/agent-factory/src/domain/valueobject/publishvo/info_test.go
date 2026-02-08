package publishvo

import (
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/enum/cdaenum"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/enum/daenum"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/valueobject/pmsvo"
)

func TestPublishInfo(t *testing.T) {
	t.Run("create publish info", func(t *testing.T) {
		info := &PublishInfo{
			CategoryIDs:      []string{"cat-1", "cat-2"},
			Description:      "Test publish description",
			PublishToWhere:   []daenum.PublishToWhere{daenum.PublishToWhereCustomSpace},
			PmsControl:       &pmsvo.PmsControlObjS{},
			PublishToBes:     []cdaenum.PublishToBe{cdaenum.PublishToBeAPIAgent},
		}

		if len(info.CategoryIDs) != 2 {
			t.Errorf("Expected 2 category IDs, got %d", len(info.CategoryIDs))
		}
		if info.CategoryIDs[0] != "cat-1" {
			t.Errorf("Expected first category ID to be 'cat-1', got '%s'", info.CategoryIDs[0])
		}
		if info.Description != "Test publish description" {
			t.Errorf("Expected description to be 'Test publish description', got '%s'", info.Description)
		}
		if len(info.PublishToWhere) != 1 {
			t.Errorf("Expected 1 publish to where, got %d", len(info.PublishToWhere))
		}
		if info.PmsControl == nil {
			t.Error("Expected PmsControl to be non-nil")
		}
		if len(info.PublishToBes) != 1 {
			t.Errorf("Expected 1 publish to be, got %d", len(info.PublishToBes))
		}
	})

	t.Run("with multiple publish targets", func(t *testing.T) {
		info := &PublishInfo{
			PublishToWhere: []daenum.PublishToWhere{
				daenum.PublishToWhereCustomSpace,
				daenum.PublishToWhereSquare,
			},
			PublishToBes: []cdaenum.PublishToBe{
				cdaenum.PublishToBeAPIAgent,
				cdaenum.PublishToBeWebSDKAgent,
				cdaenum.PublishToBeSkillAgent,
			},
		}

		if len(info.PublishToWhere) != 2 {
			t.Errorf("Expected 2 publish to where targets, got %d", len(info.PublishToWhere))
		}
		if len(info.PublishToBes) != 3 {
			t.Errorf("Expected 3 publish to be types, got %d", len(info.PublishToBes))
		}
	})

	t.Run("with empty slices", func(t *testing.T) {
		info := &PublishInfo{
			CategoryIDs:    []string{},
			PublishToWhere: []daenum.PublishToWhere{},
			PublishToBes:   []cdaenum.PublishToBe{},
		}

		if len(info.CategoryIDs) != 0 {
			t.Errorf("Expected 0 category IDs, got %d", len(info.CategoryIDs))
		}
		if len(info.PublishToWhere) != 0 {
			t.Errorf("Expected 0 publish to where, got %d", len(info.PublishToWhere))
		}
		if len(info.PublishToBes) != 0 {
			t.Errorf("Expected 0 publish to be, got %d", len(info.PublishToBes))
		}
	})

	t.Run("with nil pms control", func(t *testing.T) {
		info := &PublishInfo{
			PmsControl: nil,
		}

		if info.PmsControl != nil {
			t.Error("Expected PmsControl to be nil")
		}
	})
}
