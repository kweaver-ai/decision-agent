package cdaenum

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestBuiltIn_Constants(t *testing.T) {
	assert.Equal(t, BuiltIn(0), BuiltInNo)
	assert.Equal(t, BuiltIn(1), BuiltInYes)
}

func TestBuiltIn_EnumCheck_Valid(t *testing.T) {
	validValues := []BuiltIn{
		BuiltInNo,
		BuiltInYes,
	}

	for _, builtIn := range validValues {
		t.Run("", func(t *testing.T) {
			err := builtIn.EnumCheck()
			assert.NoError(t, err)
		})
	}
}

func TestBuiltIn_EnumCheck_Invalid(t *testing.T) {
	invalidValues := []BuiltIn{
		-1,
		2,
		100,
	}

	for _, builtIn := range invalidValues {
		t.Run("", func(t *testing.T) {
			err := builtIn.EnumCheck()
			assert.Error(t, err)
			assert.Contains(t, err.Error(), "invalid built in")
		})
	}
}

func TestBuiltIn_IsBuiltIn(t *testing.T) {
	tests := []struct {
		name     string
		builtIn  *BuiltIn
		expected bool
	}{
		{
			name:     "built in yes",
			builtIn:  func() *BuiltIn { b := BuiltInYes; return &b }(),
			expected: true,
		},
		{
			name:     "built in no",
			builtIn:  func() *BuiltIn { b := BuiltInNo; return &b }(),
			expected: false,
		},
		{
			name:     "nil pointer",
			builtIn:  nil,
			expected: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := tt.builtIn.IsBuiltIn()
			assert.Equal(t, tt.expected, result)
		})
	}
}

func TestBuiltIn_AllUnique(t *testing.T) {
	builtIns := []BuiltIn{
		BuiltInNo,
		BuiltInYes,
	}

	uniqueBuiltIns := make(map[BuiltIn]bool)
	for _, bi := range builtIns {
		assert.False(t, uniqueBuiltIns[bi], "Duplicate built-in value found: %d", bi)
		uniqueBuiltIns[bi] = true
	}
}
