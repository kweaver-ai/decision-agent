package agentinoutsvc

import (
	"testing"

	"go.uber.org/mock/gomock"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/service"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/idbaccess/idbaccessmock"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/ihttpaccess/ibizdomainacc/bizdomainaccmock"
	"github.com/stretchr/testify/assert"
)

func TestNewAgentInOutService(t *testing.T) {
	t.Run("creates service with all dependencies", func(t *testing.T) {
		ctrl := gomock.NewController(t)
		defer ctrl.Finish()

		dto := &NewAgentInOutSvcDto{
			SvcBase:        service.NewSvcBase(),
			Logger:         nil,
			AgentConfRepo:  idbaccessmock.NewMockIDataAgentConfigRepo(ctrl),
			PmsSvc:         nil,
			BizDomainHttp:  bizdomainaccmock.NewMockBizDomainHttpAcc(ctrl),
			BdAgentRelRepo: idbaccessmock.NewMockIBizDomainAgentRelRepo(ctrl),
		}

		svc := NewAgentInOutService(dto)

		assert.NotNil(t, svc)
		assert.IsType(t, &agentInOutSvc{}, svc)
	})

	t.Run("creates service with minimal dependencies", func(t *testing.T) {
		dto := &NewAgentInOutSvcDto{
			SvcBase:        service.NewSvcBase(),
			Logger:         nil,
			AgentConfRepo:  nil,
			PmsSvc:         nil,
			BizDomainHttp:  nil,
			BdAgentRelRepo: nil,
		}

		svc := NewAgentInOutService(dto)

		assert.NotNil(t, svc)
	})
}
