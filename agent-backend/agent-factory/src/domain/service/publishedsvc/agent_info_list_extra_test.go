package publishedsvc

import (
	"context"
	"errors"
	"testing"

	"go.uber.org/mock/gomock"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/service"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/published/pubedreq"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/dbaccess/pubedagentdbacc/padbret"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/idbaccess/idbaccessmock"
	"github.com/stretchr/testify/assert"
)

func TestNewPublishedService_AllDependencies(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockPubedAgentRepo := idbaccessmock.NewMockIPubedAgentRepo(ctrl)

	dto := &NewPublishedSvcDto{
		SvcBase:        service.NewSvcBase(),
		PubedAgentRepo: mockPubedAgentRepo,
	}

	svc := NewPublishedService(dto)

	assert.NotNil(t, svc)
	assert.IsType(t, &publishedSvc{}, svc)
}

func TestNewPublishedService_MinimalDependencies(t *testing.T) {
	dto := &NewPublishedSvcDto{
		SvcBase: service.NewSvcBase(),
	}

	svc := NewPublishedService(dto)

	assert.NotNil(t, svc)
	assert.IsType(t, &publishedSvc{}, svc)
}

func TestPublishedSvc_GetPubedAgentInfoList_EmptyAgentKeys(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockPubedAgentRepo := idbaccessmock.NewMockIPubedAgentRepo(ctrl)

	svc := &publishedSvc{
		SvcBase:        service.NewSvcBase(),
		pubedAgentRepo: mockPubedAgentRepo,
	}

	ctx := context.Background()
	req := &pubedreq.PAInfoListReq{
		AgentKeys: []string{},
	}

	mockPubedAgentRepo.EXPECT().GetPubedListByXx(gomock.Any(), gomock.Any()).Return(&padbret.GetPaPoListByXxRet{
		JoinPos: []*dapo.PublishedJoinPo{},
	}, nil)

	res, err := svc.GetPubedAgentInfoList(ctx, req)

	assert.NoError(t, err)
	assert.NotNil(t, res)
}

func TestPublishedSvc_GetPubedAgentInfoList_GetPubedListByXxError(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockPubedAgentRepo := idbaccessmock.NewMockIPubedAgentRepo(ctrl)

	svc := &publishedSvc{
		SvcBase:        service.NewSvcBase(),
		pubedAgentRepo: mockPubedAgentRepo,
	}

	ctx := context.Background()
	req := &pubedreq.PAInfoListReq{
		AgentKeys: []string{"agent-1"},
	}
	dbErr := errors.New("database error")

	mockPubedAgentRepo.EXPECT().GetPubedListByXx(gomock.Any(), gomock.Any()).Return(nil, dbErr)

	res, err := svc.GetPubedAgentInfoList(ctx, req)

	// Response is initialized before error check
	assert.Error(t, err)
	assert.NotNil(t, res)
	assert.Contains(t, err.Error(), "get published agent list failed")
}

func TestPublishedSvc_Struct_Init(t *testing.T) {
	svc := &publishedSvc{
		SvcBase: service.NewSvcBase(),
	}

	assert.NotNil(t, svc)
	assert.NotNil(t, svc.SvcBase)
}
