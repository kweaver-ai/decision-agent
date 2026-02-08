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

func TestNewDataAgentTplService(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	dto := &NewDaTplSvcDto{
		RedisCmp:          nil,
		SvcBase:           service.NewSvcBase(),
		AgentTplRepo:      idbaccessmock.NewMockIDataAgentTplRepo(ctrl),
		PublishedTplRepo:  idbaccessmock.NewMockIPublishedTplRepo(ctrl),
		AgentConfRepo:     idbaccessmock.NewMockIDataAgentConfigRepo(ctrl),
		Logger:            nil,
		UmHttp:            httpaccmock.NewMockUmHttpAcc(ctrl),
		CategorySvc:       nil,
		ProductRepo:       idbaccessmock.NewMockIProductRepo(ctrl),
		CategoryRepo:      idbaccessmock.NewMockICategoryRepo(ctrl),
		PmsSvc:            nil,
		BizDomainHttp:     bizdomainaccmock.NewMockBizDomainHttpAcc(ctrl),
		BdAgentTplRelRepo: idbaccessmock.NewMockIBizDomainAgentTplRelRepo(ctrl),
	}

	svc := NewDataAgentTplService(dto)

	assert.NotNil(t, svc)
}
