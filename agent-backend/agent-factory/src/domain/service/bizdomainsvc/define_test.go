package bizdomainsvc

import (
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/service"
	"github.com/stretchr/testify/assert"
)

func TestNewBizDomainService(t *testing.T) {
	dto := &NewBizDomainSvcDto{
		SvcBase: service.NewSvcBase(),
	}

	svc := NewBizDomainService(dto)

	assert.NotNil(t, svc)
}
