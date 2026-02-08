package publishedsvc

import (
	"testing"

	"go.uber.org/mock/gomock"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/service"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/idbaccess/idbaccessmock"
	"github.com/stretchr/testify/assert"
)

func TestNewPublishedService(t *testing.T) {
	t.Run("creates service with all dependencies", func(t *testing.T) {
		ctrl := gomock.NewController(t)
		defer ctrl.Finish()

		dto := &NewPublishedSvcDto{
			SvcBase:          service.NewSvcBase(),
			AgentTplRepo:     idbaccessmock.NewMockIDataAgentTplRepo(ctrl),
			PublishedTplRepo: idbaccessmock.NewMockIPublishedTplRepo(ctrl),
			PubedAgentRepo:   idbaccessmock.NewMockIPubedAgentRepo(ctrl),
			ProductRepo:      idbaccessmock.NewMockIProductRepo(ctrl),
		}

		svc := NewPublishedService(dto)

		assert.NotNil(t, svc)
		assert.IsType(t, &publishedSvc{}, svc)
	})

	t.Run("creates service with minimal dependencies", func(t *testing.T) {
		dto := &NewPublishedSvcDto{
			SvcBase:          service.NewSvcBase(),
			AgentTplRepo:     nil,
			PublishedTplRepo: nil,
			PubedAgentRepo:   nil,
			ProductRepo:      nil,
			UmHttp:           nil,
			AuthZHttp:        nil,
			PmsSvc:           nil,
			BizDomainHttp:    nil,
		}

		svc := NewPublishedService(dto)

		assert.NotNil(t, svc)
	})
}
