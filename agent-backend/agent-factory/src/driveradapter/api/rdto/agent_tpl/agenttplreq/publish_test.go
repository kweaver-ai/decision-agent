package agenttplreq

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestNewPublishReq(t *testing.T) {
	req := NewPublishReq()

	assert.NotNil(t, req)
	assert.NotNil(t, req.UpdatePublishInfoReq)
	assert.Empty(t, req.BusinessDomainID)
}

func TestPublishReq_GetErrMsgMap(t *testing.T) {
	req := &PublishReq{}
	errMap := req.GetErrMsgMap()

	assert.NotEmpty(t, errMap)
	assert.Equal(t, `"Agent ID 不能为空`, errMap["AgentID.required"])
}

func TestPublishReq_ReqCheck(t *testing.T) {
	t.Run("valid request", func(t *testing.T) {
		req := &PublishReq{}
		err := req.ReqCheck()
		assert.NoError(t, err)
	})

	t.Run("with business domain", func(t *testing.T) {
		req := &PublishReq{
			BusinessDomainID: "bd-123",
		}
		err := req.ReqCheck()
		assert.NoError(t, err)
	})
}

func TestPublishReq_StructFields(t *testing.T) {
	req := &PublishReq{
		BusinessDomainID: "bd-456",
	}

	assert.Equal(t, "bd-456", req.BusinessDomainID)
}

func TestPublishReq_Empty(t *testing.T) {
	req := &PublishReq{}

	assert.Empty(t, req.BusinessDomainID)
}

func TestPublishReq_WithBusinessDomainID(t *testing.T) {
	bdIDs := []string{
		"bd-001",
		"business-domain-123",
		"",
	}

	for _, bdID := range bdIDs {
		req := &PublishReq{
			BusinessDomainID: bdID,
		}
		assert.Equal(t, bdID, req.BusinessDomainID)
	}
}
