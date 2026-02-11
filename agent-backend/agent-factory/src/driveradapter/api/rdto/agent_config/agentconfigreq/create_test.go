package agentconfigreq

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestCreateReq_GetErrMsgMap(t *testing.T) {
	req := &CreateReq{}

	errMap := req.GetErrMsgMap()

	assert.NotNil(t, errMap)
	assert.Contains(t, errMap, "Key.max")
	assert.Equal(t, `"key"长度不能超过50`, errMap["Key.max"])
}

