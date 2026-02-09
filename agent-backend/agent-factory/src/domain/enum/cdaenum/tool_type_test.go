package cdaenum

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestToolType_Constants(t *testing.T) {
	assert.Equal(t, ToolType("tool"), ToolTypeTool)
	assert.Equal(t, ToolType("agent"), ToolTypeAgent)
}

func TestToolType_EnumCheck_Valid(t *testing.T) {
	validTypes := []ToolType{
		ToolTypeTool,
		ToolTypeAgent,
	}

	for _, toolType := range validTypes {
		t.Run(string(toolType), func(t *testing.T) {
			err := toolType.EnumCheck()
			assert.NoError(t, err)
		})
	}
}

func TestToolType_EnumCheck_Invalid(t *testing.T) {
	invalidType := ToolType("invalid_type")
	err := invalidType.EnumCheck()
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "invalid tool type")
}

func TestToolType_EnumCheck_Empty(t *testing.T) {
	emptyType := ToolType("")
	err := emptyType.EnumCheck()
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "invalid tool type")
}

func TestToolType_AllUnique(t *testing.T) {
	toolTypes := []ToolType{
		ToolTypeTool,
		ToolTypeAgent,
	}

	uniqueTypes := make(map[ToolType]bool)
	for _, tt := range toolTypes {
		assert.False(t, uniqueTypes[tt], "Duplicate tool type found: %s", tt)
		uniqueTypes[tt] = true
	}
}
