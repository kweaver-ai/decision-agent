package daenum

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestDatasetObjectType_EnumCheck_Valid(t *testing.T) {
	err := DatasetObjTypeDir.EnumCheck()
	assert.NoError(t, err)
}

func TestDatasetObjectType_EnumCheck_Invalid(t *testing.T) {
	tests := []struct {
		name string
		ot   DatasetObjectType
	}{
		{"empty", ""},
		{"invalid", "invalid_type"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := tt.ot.EnumCheck()
			assert.Error(t, err)
			assert.Contains(t, err.Error(), "invalid object type")
		})
	}
}

func TestDatasetObjectType_String(t *testing.T) {
	assert.Equal(t, "dir", string(DatasetObjTypeDir))
}
