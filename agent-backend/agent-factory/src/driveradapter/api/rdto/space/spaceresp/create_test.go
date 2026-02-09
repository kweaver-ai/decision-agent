package spaceresp

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestNewCreateResp(t *testing.T) {
	resp := NewCreateResp()

	assert.NotNil(t, resp)
	assert.Empty(t, resp.ID)
}

func TestCreateResp_WithID(t *testing.T) {
	resp := &CreateResp{
		ID: "space123",
	}

	assert.Equal(t, "space123", resp.ID)
}

func TestCreateResp_NewAndSetID(t *testing.T) {
	resp := NewCreateResp()
	resp.ID = "space456"

	assert.Equal(t, "space456", resp.ID)
}

func TestCreateResp_EmptyID(t *testing.T) {
	resp := &CreateResp{
		ID: "",
	}

	assert.Empty(t, resp.ID)
}

func TestCreateResp_MultipleInstances(t *testing.T) {
	resp1 := NewCreateResp()
	resp2 := NewCreateResp()

	resp1.ID = "space1"
	resp2.ID = "space2"

	assert.Equal(t, "space1", resp1.ID)
	assert.Equal(t, "space2", resp2.ID)
	assert.NotEqual(t, resp1.ID, resp2.ID)
}
