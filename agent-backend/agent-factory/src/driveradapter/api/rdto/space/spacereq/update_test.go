package spacereq

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestNewUpdateReq(t *testing.T) {
	req := NewUpdateReq()

	assert.NotNil(t, req)
	assert.Empty(t, req.Name)
	assert.Empty(t, req.Profile)
}

func TestUpdateReq_GetErrMsgMap(t *testing.T) {
	req := &UpdateReq{}

	errMsgMap := req.GetErrMsgMap()

	assert.NotNil(t, errMsgMap)
	assert.Equal(t, 3, len(errMsgMap))
	assert.Equal(t, `"name"不能为空`, errMsgMap["Name.required"])
	assert.Equal(t, `"name"长度不能超过50个字符`, errMsgMap["Name.max"])
	assert.Equal(t, `"profile"长度不能超过100个字符`, errMsgMap["Profile.max"])
}

func TestUpdateReq_CustomCheck(t *testing.T) {
	req := &UpdateReq{}

	err := req.CustomCheck()
	assert.NoError(t, err)
}

func TestUpdateReq_WithValues(t *testing.T) {
	req := &UpdateReq{
		Name:    "Test Space",
		Profile: "Test profile",
	}

	assert.Equal(t, "Test Space", req.Name)
	assert.Equal(t, "Test profile", req.Profile)
}

func TestUpdateReq_WithEmptyValues(t *testing.T) {
	req := &UpdateReq{
		Name:    "",
		Profile: "",
	}

	assert.Empty(t, req.Name)
	assert.Empty(t, req.Profile)
}

func TestUpdateReq_WithNameOnly(t *testing.T) {
	req := &UpdateReq{
		Name: "Space Name",
	}

	assert.Equal(t, "Space Name", req.Name)
	assert.Empty(t, req.Profile)
}

func TestUpdateReq_WithProfileOnly(t *testing.T) {
	req := &UpdateReq{
		Profile: "Space profile description",
	}

	assert.Empty(t, req.Name)
	assert.Equal(t, "Space profile description", req.Profile)
}

func TestUpdateReq_NameMaxLength(t *testing.T) {
	req := &UpdateReq{
		Name: generateString(50),
	}

	assert.Equal(t, 50, len(req.Name))
}

func TestUpdateReq_ProfileMaxLength(t *testing.T) {
	req := &UpdateReq{
		Profile: generateString(100),
	}

	assert.Equal(t, 100, len(req.Profile))
}

func TestUpdateReq_GetErrMsgMapConsistency(t *testing.T) {
	req1 := &UpdateReq{}
	req2 := &UpdateReq{Name: "test"}

	map1 := req1.GetErrMsgMap()
	map2 := req2.GetErrMsgMap()

	// Both should return the same error map
	assert.Equal(t, map1, map2)
	assert.Equal(t, 3, len(map1))
}

// Helper function to generate strings of specific length
func generateString(length int) string {
	result := make([]byte, length)
	for i := range result {
		result[i] = 'a'
	}
	return string(result)
}
