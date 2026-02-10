package spacereq

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestMemberListReq_GetErrMsgMap(t *testing.T) {
	req := &MemberListReq{}
	errMap := req.GetErrMsgMap()

	assert.NotNil(t, errMap)
}

func TestMemberListReq_StructFields(t *testing.T) {
	req := &MemberListReq{}
	assert.NotNil(t, req)
}

func TestMemberListReq_Empty(t *testing.T) {
	req := &MemberListReq{}
	assert.NotNil(t, req)
}
