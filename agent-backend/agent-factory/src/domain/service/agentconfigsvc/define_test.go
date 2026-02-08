package v3agentconfigsvc

import (
	"testing"

	"go.uber.org/mock/gomock"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/service"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/idbaccess/idbaccessmock"
	"github.com/stretchr/testify/assert"
)

func TestNewDataAgentConfigService(t *testing.T) {
	t.Run("creates service with all dependencies", func(t *testing.T) {
		ctrl := gomock.NewController(t)
		defer ctrl.Finish()

		dto := &NewDaConfSvcDto{
			SvcBase:           service.NewSvcBase(),
			AgentConfRepo:     idbaccessmock.NewMockIDataAgentConfigRepo(ctrl),
			AgentTplRepo:      idbaccessmock.NewMockIDataAgentTplRepo(ctrl),
			ReleaseRepo:       idbaccessmock.NewMockIReleaseRepo(ctrl),
			PubedAgentRepo:    idbaccessmock.NewMockIPubedAgentRepo(ctrl),
			ProductRepo:       idbaccessmock.NewMockIProductRepo(ctrl),
			SpaceResourceRepo: idbaccessmock.NewMockISpaceResourceRepo(ctrl),
			BdAgentRelRepo:    idbaccessmock.NewMockIBizDomainAgentRelRepo(ctrl),
			BdAgentTplRelRepo: idbaccessmock.NewMockIBizDomainAgentTplRelRepo(ctrl),
		}

		svc := NewDataAgentConfigService(dto)

		assert.NotNil(t, svc)
		assert.IsType(t, &dataAgentConfigSvc{}, svc)
	})

	t.Run("creates service with minimal dependencies", func(t *testing.T) {
		dto := &NewDaConfSvcDto{
			SvcBase:           service.NewSvcBase(),
			AgentConfRepo:     nil,
			AgentTplRepo:      nil,
			ReleaseRepo:       nil,
			PubedAgentRepo:    nil,
			ProductRepo:       nil,
			SpaceResourceRepo: nil,
			BdAgentRelRepo:    nil,
			BdAgentTplRelRepo: nil,
		}

		svc := NewDataAgentConfigService(dto)

		assert.NotNil(t, svc)
	})
}
