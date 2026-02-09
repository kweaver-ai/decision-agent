package comvalobj

import (
	"encoding/json"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestPagination_New(t *testing.T) {
	pagination := &Pagination{
		Offset: 0,
		Limit:  10,
	}

	assert.NotNil(t, pagination)
	assert.Equal(t, 0, pagination.Offset)
	assert.Equal(t, 10, pagination.Limit)
}

func TestPagination_DefaultValues(t *testing.T) {
	pagination := &Pagination{}

	assert.NotNil(t, pagination)
	assert.Equal(t, 0, pagination.Offset)
	assert.Equal(t, 0, pagination.Limit)
}

func TestPagination_WithLargeValues(t *testing.T) {
	pagination := &Pagination{
		Offset: 1000,
		Limit:  5000,
	}

	assert.Equal(t, 1000, pagination.Offset)
	assert.Equal(t, 5000, pagination.Limit)
}

func TestPagination_JSONSerialization(t *testing.T) {
	pagination := &Pagination{
		Offset: 20,
		Limit:  50,
	}

	jsonBytes, err := json.Marshal(pagination)
	require.NoError(t, err)

	var deserialized Pagination
	err = json.Unmarshal(jsonBytes, &deserialized)
	require.NoError(t, err)

	assert.Equal(t, pagination.Offset, deserialized.Offset)
	assert.Equal(t, pagination.Limit, deserialized.Limit)
}

func TestPagination_JSONTags(t *testing.T) {
	pagination := &Pagination{
		Offset: 10,
		Limit:  25,
	}

	jsonBytes, err := json.Marshal(pagination)
	require.NoError(t, err)

	jsonStr := string(jsonBytes)
	assert.Contains(t, jsonStr, `"offset"`)
	assert.Contains(t, jsonStr, `"limit"`)
	assert.Contains(t, jsonStr, `10`)
	assert.Contains(t, jsonStr, `25`)
}

func TestPagination_WithNegativeValues(t *testing.T) {
	pagination := &Pagination{
		Offset: -10,
		Limit:  -5,
	}

	assert.Equal(t, -10, pagination.Offset)
	assert.Equal(t, -5, pagination.Limit)
}

func TestPagination_WithZeroLimit(t *testing.T) {
	pagination := &Pagination{
		Offset: 100,
		Limit:  0,
	}

	assert.Equal(t, 100, pagination.Offset)
	assert.Equal(t, 0, pagination.Limit)
}
