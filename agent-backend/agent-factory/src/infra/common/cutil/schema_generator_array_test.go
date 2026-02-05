package cutil

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestCreateDynamicStruct_WithArrays(t *testing.T) {
	schemaStr := `{
		"names": {
			"type": "array",
			"items": {
				"type": "string"
			}
		},
		"scores": {
			"type": "array",
			"items": {
				"type": "number"
			}
		},
		"flags": {
			"type": "array",
			"items": {
				"type": "boolean"
			}
		},
		"counts": {
			"type": "array",
			"items": {
				"type": "integer"
			}
		},
		"dynamic": {
			"type": "array",
			"items": {
				"type": "object",
				"properties": {
					"key": {"type": "string"}
				}
			}
		}
	}`

	typ, err := CreateDynamicStruct(schemaStr)

	assert.NoError(t, err, "CreateDynamicStruct should not return error for arrays")
	assert.NotNil(t, typ, "CreateDynamicStruct should return non-nil type")
	assert.Equal(t, "struct", typ.Kind().String(), "CreateDynamicStruct should return struct type")
	assert.Equal(t, 5, typ.NumField(), "CreateDynamicStruct should return struct with 5 fields")

	for i := 0; i < typ.NumField(); i++ {
		field := typ.Field(i)
		assert.Equal(t, "slice", field.Type.Kind().String(), "All fields should be slice type")
	}
}

func TestCreateDynamicStruct_ArrayWithObjectItems(t *testing.T) {
	schemaStr := `{
		"items": {
			"type": "array",
			"items": {
				"type": "object",
				"properties": {
					"id": {"type": "integer"},
					"name": {"type": "string"}
				}
			}
		}
	}`

	typ, err := CreateDynamicStruct(schemaStr)

	assert.NoError(t, err, "CreateDynamicStruct should not return error for array with object items")
	assert.NotNil(t, typ, "CreateDynamicStruct should return non-nil type")
	assert.Equal(t, 1, typ.NumField(), "CreateDynamicStruct should return struct with 1 field")

	field := typ.Field(0)
	assert.Equal(t, "slice", field.Type.Kind().String(), "Field should be slice type")

	elemType := field.Type.Elem()
	assert.Equal(t, "struct", elemType.Kind().String(), "Slice element should be struct type")
	assert.Equal(t, 2, elemType.NumField(), "Struct should have 2 fields")
}
