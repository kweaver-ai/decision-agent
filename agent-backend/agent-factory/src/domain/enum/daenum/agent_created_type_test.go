package daenum

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestAgentCreatedType_EnumCheck_Valid(t *testing.T) {
	tests := []struct {
		name string
		ct   AgentCreatedType
	}{
		{"create", AgentCreatedTypeCreate},
		{"copy", AgentCreatedTypeCopy},
		{"import", AgentCreatedTypeImport},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := tt.ct.EnumCheck()
			assert.NoError(t, err)
		})
	}
}

func TestAgentCreatedType_EnumCheck_Invalid(t *testing.T) {
	tests := []struct {
		name string
		ct   AgentCreatedType
	}{
		{"empty", ""},
		{"invalid", "invalid_type"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := tt.ct.EnumCheck()
			assert.Error(t, err)
			assert.Contains(t, err.Error(), "invalid agent created type")
		})
	}
}

func TestAgentCreatedType_String(t *testing.T) {
	assert.Equal(t, "create", string(AgentCreatedTypeCreate))
	assert.Equal(t, "copy", string(AgentCreatedTypeCopy))
	assert.Equal(t, "import", string(AgentCreatedTypeImport))
}
