package agentconfigreq

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestUpdateReq_GetErrMsgMap(t *testing.T) {
	req := &UpdateReq{}

	errMap := req.GetErrMsgMap()

	// Verify the error message map is not nil
	assert.NotNil(t, errMap)
}

