package daenum

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestDatasetObjectType_Constants(t *testing.T) {
	assert.Equal(t, DatasetObjectType("dir"), DatasetObjTypeDir)
}

func TestDatasetObjectType_EnumCheck_Valid(t *testing.T) {
	err := DatasetObjTypeDir.EnumCheck()
	assert.NoError(t, err)
}

func TestDatasetObjectType_EnumCheck_Invalid(t *testing.T) {
	invalidType := DatasetObjectType("invalid_type")
	err := invalidType.EnumCheck()
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "invalid object type")
}

func TestDatasetObjectType_EnumCheck_Empty(t *testing.T) {
	emptyType := DatasetObjectType("")
	err := emptyType.EnumCheck()
	assert.Error(t, err)
}

func TestDatasetObjectType_StringValue(t *testing.T) {
	result := string(DatasetObjTypeDir)
	assert.Equal(t, "dir", result)
}
