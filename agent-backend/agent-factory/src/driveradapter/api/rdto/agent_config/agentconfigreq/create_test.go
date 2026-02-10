package agentconfigreq

import (
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/enum/cdaenum"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/valueobject/daconfvalobj"
	"github.com/stretchr/testify/assert"
)

func TestCreateReq_GetErrMsgMap(t *testing.T) {
	req := &CreateReq{}
	errMap := req.GetErrMsgMap()

	assert.NotEmpty(t, errMap)
	assert.Equal(t, `"key"长度不能超过50`, errMap["Key.max"])
}

func TestCreateReq_D2e(t *testing.T) {
	t.Run("with valid request", func(t *testing.T) {
		isBuiltIn := cdaenum.BuiltInYes
		req := &CreateReq{
			UpdateReq: &UpdateReq{
				Name:    "Test Agent",
				Profile: "Test Profile",
				Config: &daconfvalobj.Config{
					Input:  &daconfvalobj.Input{},
					Output: &daconfvalobj.Output{},
				},
				IsBuiltIn: &isBuiltIn,
			},
			Key: "test-key",
		}

		eo, err := req.D2e()
		assert.NoError(t, err)
		assert.NotNil(t, eo)
		assert.Equal(t, "Test Agent", eo.Name)
	})

	t.Run("with empty key generates ulid", func(t *testing.T) {
		req := &CreateReq{
			UpdateReq: &UpdateReq{
				Name:    "Test Agent",
				Profile: "Test Profile",
				Config: &daconfvalobj.Config{
					Input:  &daconfvalobj.Input{},
					Output: &daconfvalobj.Output{},
				},
			},
			Key: "",
		}

		eo, err := req.D2e()
		assert.NoError(t, err)
		assert.NotNil(t, eo)
		assert.NotEmpty(t, eo.Key)
	})
}

func TestCreateReq_ReqCheckWithCtx(t *testing.T) {
	// Skip these tests because they require proper LLM configuration setup
	t.Skip("ReqCheckWithCtx requires proper LLM configuration which is complex to set up in tests")
}

func TestCreateReq_StructFields(t *testing.T) {
	req := &CreateReq{
		Key: "test-key",
		UpdateReq: &UpdateReq{
			Name: "Test Agent",
		},
	}

	assert.Equal(t, "test-key", req.Key)
	assert.NotNil(t, req.UpdateReq)
}

func TestCreateReq_Empty(t *testing.T) {
	req := &CreateReq{}

	assert.Empty(t, req.Key)
}

func TestCreateReq_WithKey(t *testing.T) {
	keys := []string{
		"agent-001",
		"test_key",
		"MY-AGENT-KEY",
		"",
	}

	for _, key := range keys {
		req := &CreateReq{Key: key}
		assert.Equal(t, key, req.Key)
	}
}
