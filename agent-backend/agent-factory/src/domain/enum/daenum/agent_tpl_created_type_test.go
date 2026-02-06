package daenum

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestAgentTplCreatedType_EnumCheck_Valid(t *testing.T) {
	tests := []struct {
		name string
		ct   AgentTplCreatedType
	}{
		{"copy from agent", AgentTplCreatedTypeCopyFromAgent},
		{"copy from tpl", AgentTplCreatedTypeCopyFromTpl},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := tt.ct.EnumCheck()
			assert.NoError(t, err)
		})
	}
}

func TestAgentTplCreatedType_EnumCheck_Invalid(t *testing.T) {
	tests := []struct {
		name string
		ct   AgentTplCreatedType
	}{
		{"empty", ""},
		{"invalid", "invalid_type"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := tt.ct.EnumCheck()
			assert.Error(t, err)
			assert.Contains(t, err.Error(), "无效的AgentTplCreatedType")
		})
	}
}

func TestAgentTplCreatedType_String(t *testing.T) {
	assert.Equal(t, "copy_from_agent", string(AgentTplCreatedTypeCopyFromAgent))
	assert.Equal(t, "copy_from_tpl", string(AgentTplCreatedTypeCopyFromTpl))
}
