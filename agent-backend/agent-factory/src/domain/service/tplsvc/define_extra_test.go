package tplsvc

import (
	"testing"

	"go.uber.org/mock/gomock"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/service"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/idbaccess/idbaccessmock"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/ihttpaccess/ibizdomainacc/bizdomainaccmock"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/ihttpaccess/iumacc/httpaccmock"
	"github.com/stretchr/testify/assert"
)

func TestNewDataAgentTplService_AdditionalCases(t *testing.T) {
	t.Run("creates service with partial dependencies", func(t *testing.T) {
		ctrl := gomock.NewController(t)
		defer ctrl.Finish()

		dto := &NewDaTplSvcDto{
			SvcBase:           service.NewSvcBase(),
			AgentTplRepo:      idbaccessmock.NewMockIDataAgentTplRepo(ctrl),
			PublishedTplRepo:  nil,
			AgentConfRepo:     nil,
			Logger:            nil,
			UmHttp:            httpaccmock.NewMockUmHttpAcc(ctrl),
			CategorySvc:       nil,
			ProductRepo:       nil,
			CategoryRepo:      nil,
			PmsSvc:            nil,
			BizDomainHttp:     nil,
			BdAgentTplRelRepo: nil,
		}

		svc := NewDataAgentTplService(dto)

		assert.NotNil(t, svc)
		assert.IsType(t, &dataAgentTplSvc{}, svc)
	})

	t.Run("creates service with only required fields", func(t *testing.T) {
		dto := &NewDaTplSvcDto{
			SvcBase: service.NewSvcBase(),
		}

		svc := NewDataAgentTplService(dto)

		assert.NotNil(t, svc)
		assert.IsType(t, &dataAgentTplSvc{}, svc)
	})

	t.Run("creates service with all mock dependencies", func(t *testing.T) {
		ctrl := gomock.NewController(t)
		defer ctrl.Finish()

		dto := &NewDaTplSvcDto{
			SvcBase:           service.NewSvcBase(),
			AgentTplRepo:      idbaccessmock.NewMockIDataAgentTplRepo(ctrl),
			PublishedTplRepo:  idbaccessmock.NewMockIPublishedTplRepo(ctrl),
			AgentConfRepo:     idbaccessmock.NewMockIDataAgentConfigRepo(ctrl),
			UmHttp:            httpaccmock.NewMockUmHttpAcc(ctrl),
			ProductRepo:       idbaccessmock.NewMockIProductRepo(ctrl),
			CategoryRepo:      idbaccessmock.NewMockICategoryRepo(ctrl),
			BizDomainHttp:     bizdomainaccmock.NewMockBizDomainHttpAcc(ctrl),
			BdAgentTplRelRepo: idbaccessmock.NewMockIBizDomainAgentTplRelRepo(ctrl),
		}

		svc := NewDataAgentTplService(dto)

		assert.NotNil(t, svc)
	})

	t.Run("creates service with nil SvcBase", func(t *testing.T) {
		dto := &NewDaTplSvcDto{
			SvcBase: nil,
		}

		svc := NewDataAgentTplService(dto)

		assert.NotNil(t, svc)
		assert.IsType(t, &dataAgentTplSvc{}, svc)
	})

	t.Run("multiple service instances are independent", func(t *testing.T) {
		ctrl := gomock.NewController(t)
		defer ctrl.Finish()

		dto1 := &NewDaTplSvcDto{
			SvcBase:      service.NewSvcBase(),
			AgentTplRepo: idbaccessmock.NewMockIDataAgentTplRepo(ctrl),
		}

		dto2 := &NewDaTplSvcDto{
			SvcBase:      service.NewSvcBase(),
			AgentTplRepo: idbaccessmock.NewMockIDataAgentTplRepo(ctrl),
		}

		svc1 := NewDataAgentTplService(dto1)
		svc2 := NewDataAgentTplService(dto2)

		assert.NotNil(t, svc1)
		assert.NotNil(t, svc2)
		assert.NotSame(t, svc1, svc2)
	})
}

func TestDataAgentTplSvc_Interface(t *testing.T) {
	t.Run("implements expected interface", func(t *testing.T) {
		ctrl := gomock.NewController(t)
		defer ctrl.Finish()

		dto := &NewDaTplSvcDto{
			SvcBase:      service.NewSvcBase(),
			AgentTplRepo: idbaccessmock.NewMockIDataAgentTplRepo(ctrl),
		}

		svc := NewDataAgentTplService(dto)

		// Verify the service is not nil and has the expected type
		assert.NotNil(t, svc)
		assert.IsType(t, &dataAgentTplSvc{}, svc)
	})
}
