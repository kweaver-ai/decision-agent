package daconfvalobj

import (
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/enum/cdaenum"
	"github.com/stretchr/testify/assert"
)

func TestRelatedQuestion_ValObjCheck(t *testing.T) {
	rq := &RelatedQuestion{}

	// This struct has no validation, so it always passes
	err := rq.ValObjCheck()
	assert.NoError(t, err)
}

func TestRelatedQuestion_IsEnabled(t *testing.T) {
	rq := &RelatedQuestion{
		IsEnabled: true,
	}

	assert.True(t, rq.IsEnabled)
}

func TestRelatedQuestion_Disabled(t *testing.T) {
	rq := &RelatedQuestion{
		IsEnabled: false,
	}

	assert.False(t, rq.IsEnabled)
}

func TestRelatedQuestion_Empty(t *testing.T) {
	rq := &RelatedQuestion{}

	assert.False(t, rq.IsEnabled)
}

func TestField_ValObjCheck_Valid(t *testing.T) {
	tests := []struct {
		name string
		f    *Field
	}{
		{
			name: "string type field",
			f: &Field{
				Name: "test_field",
				Type: cdaenum.InputFieldTypeString,
				Desc: "test description",
			},
		},
		{
			name: "file type field",
			f: &Field{
				Name: "file_field",
				Type: cdaenum.InputFieldTypeFile,
				Desc: "file upload field",
			},
		},
		{
			name: "object type field",
			f: &Field{
				Name: "object_field",
				Type: cdaenum.InputFieldTypeJSONObject,
				Desc: "json object field",
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := tt.f.ValObjCheck()
			assert.NoError(t, err)
		})
	}
}

func TestField_ValObjCheck_EmptyName(t *testing.T) {
	f := &Field{
		Name: "",
		Type: cdaenum.InputFieldTypeString,
	}

	err := f.ValObjCheck()
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "name is required")
}

func TestField_ValObjCheck_InvalidType(t *testing.T) {
	f := &Field{
		Name: "test",
		Type: cdaenum.InputFieldType("invalid_type"),
	}

	err := f.ValObjCheck()
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "type is invalid")
}

func TestField_GetErrMsgMap(t *testing.T) {
	f := &Field{}

	errMap := f.GetErrMsgMap()
	assert.NotNil(t, errMap)
	assert.Equal(t, `"name"不能为空`, errMap["Name.required"])
}

func TestField_Fields(t *testing.T) {
	f := &Field{
		Name: "my_field",
		Type: cdaenum.InputFieldTypeString,
		Desc: "my field description",
	}

	assert.Equal(t, "my_field", f.Name)
	assert.Equal(t, cdaenum.InputFieldTypeString, f.Type)
	assert.Equal(t, "my field description", f.Desc)
}

func TestField_Empty(t *testing.T) {
	f := &Field{}

	assert.Empty(t, f.Name)
	assert.Equal(t, cdaenum.InputFieldType(""), f.Type)
	assert.Empty(t, f.Desc)
}
