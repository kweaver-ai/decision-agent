package agentinoutreq

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestImportType_Constants(t *testing.T) {
	assert.Equal(t, ImportType("upsert"), ImportTypeUpsert)
	assert.Equal(t, ImportType("create"), ImportTypeCreate)
}

func TestImportType_String(t *testing.T) {
	tests := []struct {
		name     string
		importType ImportType
		expected string
	}{
		{
			name:     "upsert type",
			importType: ImportTypeUpsert,
			expected: "upsert",
		},
		{
			name:     "create type",
			importType: ImportTypeCreate,
			expected: "create",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := tt.importType.String()
			assert.Equal(t, tt.expected, result)
		})
	}
}

func TestImportType_EnumCheck_Valid(t *testing.T) {
	tests := []struct {
		name     string
		importType ImportType
		wantErr  bool
	}{
		{
			name:     "upsert - valid",
			importType: ImportTypeUpsert,
			wantErr:  false,
		},
		{
			name:     "create - valid",
			importType: ImportTypeCreate,
			wantErr:  false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := tt.importType.EnumCheck()

			if tt.wantErr {
				assert.Error(t, err)
			} else {
				assert.NoError(t, err)
			}
		})
	}
}

func TestImportType_EnumCheck_Invalid(t *testing.T) {
	invalidType := ImportType("invalid_type")

	err := invalidType.EnumCheck()

	assert.Error(t, err)
	assert.Contains(t, err.Error(), "invalid import type")
}

func TestImportType_Empty(t *testing.T) {
	emptyType := ImportType("")

	err := emptyType.EnumCheck()

	assert.Error(t, err)
	assert.Contains(t, err.Error(), "invalid import type")
}

func TestImportType_CustomValues(t *testing.T) {
	// Test that custom string values can be created
	customType := ImportType("custom")

	assert.Equal(t, ImportType("custom"), customType)
	assert.Equal(t, "custom", customType.String())
}

func TestImportType_Comparison(t *testing.T) {
	upsert1 := ImportTypeUpsert
	upsert2 := ImportType("upsert")
	create := ImportTypeCreate

	assert.Equal(t, upsert1, upsert2)
	assert.NotEqual(t, upsert1, create)
	assert.True(t, upsert1 == ImportTypeUpsert)
	assert.False(t, upsert1 == create)
}

func TestImportType_InSlice(t *testing.T) {
	types := []ImportType{
		ImportTypeUpsert,
		ImportTypeCreate,
		ImportTypeUpsert,
	}

	assert.Len(t, types, 3)
	assert.Equal(t, ImportTypeUpsert, types[0])
	assert.Equal(t, ImportTypeCreate, types[1])
	assert.Equal(t, ImportTypeUpsert, types[2])
}
