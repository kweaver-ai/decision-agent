package bizdomainsvc

import (
	"context"
	"errors"
	"testing"

	"go.uber.org/mock/gomock"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/service"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/cmp/icmp/cmpmock"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/idbaccess/idbaccessmock"
	"github.com/stretchr/testify/assert"
)

func TestBizDomainSvc_FixMissingAgentTplRel_GetAllIDsError(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockAgentTplRepo := idbaccessmock.NewMockIDataAgentTplRepo(ctrl)
	mockBdAgentTplRelRepo := idbaccessmock.NewMockIBizDomainAgentTplRelRepo(ctrl)
	mockLogger := cmpmock.NewMockLogger(ctrl)

	svc := &BizDomainSvc{
		SvcBase: service.NewSvcBase(),
		logger:  mockLogger,
	}

	ctx := context.Background()
	dbErr := errors.New("database query failed")

	mockAgentTplRepo.EXPECT().GetAllIDs(gomock.Any()).Return(nil, dbErr)

	resp, err := svc.FixMissingAgentTplRel(ctx, mockAgentTplRepo, mockBdAgentTplRelRepo)

	assert.Error(t, err)
	assert.Nil(t, resp)
	assert.Contains(t, err.Error(), "get all agent tpl ids failed")
}

func TestBizDomainSvc_FixMissingAgentTplRel_NoAgentTplData(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockAgentTplRepo := idbaccessmock.NewMockIDataAgentTplRepo(ctrl)
	mockBdAgentTplRelRepo := idbaccessmock.NewMockIBizDomainAgentTplRelRepo(ctrl)
	mockLogger := cmpmock.NewMockLogger(ctrl)

	svc := &BizDomainSvc{
		SvcBase: service.NewSvcBase(),
		logger:  mockLogger,
	}

	ctx := context.Background()

	mockAgentTplRepo.EXPECT().GetAllIDs(gomock.Any()).Return([]int64{}, nil)
	mockLogger.EXPECT().Infoln(gomock.Any())

	resp, err := svc.FixMissingAgentTplRel(ctx, mockAgentTplRepo, mockBdAgentTplRelRepo)

	assert.NoError(t, err)
	assert.NotNil(t, resp)
	assert.Equal(t, 0, resp.FixedCount)
	assert.Empty(t, resp.FixedIDs)
}

func TestBizDomainSvc_FixMissingAgentTplRel_BeginTxError(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockAgentTplRepo := idbaccessmock.NewMockIDataAgentTplRepo(ctrl)
	mockBdAgentTplRelRepo := idbaccessmock.NewMockIBizDomainAgentTplRelRepo(ctrl)
	mockLogger := cmpmock.NewMockLogger(ctrl)

	svc := &BizDomainSvc{
		SvcBase: service.NewSvcBase(),
		logger:  mockLogger,
	}

	ctx := context.Background()
	agentTplIDs := []int64{1, 2, 3}
	txErr := errors.New("transaction begin failed")

	mockAgentTplRepo.EXPECT().GetAllIDs(gomock.Any()).Return(agentTplIDs, nil)
	mockBdAgentTplRelRepo.EXPECT().BeginTx(gomock.Any()).Return(nil, txErr)

	resp, err := svc.FixMissingAgentTplRel(ctx, mockAgentTplRepo, mockBdAgentTplRelRepo)

	assert.Error(t, err)
	assert.Nil(t, resp)
	assert.Contains(t, err.Error(), "begin tx failed")
}

func TestBizDomainSvc_FixMissingAgentTplRel_GetByBizDomainIDError_BeginTxFails(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockAgentTplRepo := idbaccessmock.NewMockIDataAgentTplRepo(ctrl)
	mockBdAgentTplRelRepo := idbaccessmock.NewMockIBizDomainAgentTplRelRepo(ctrl)
	mockLogger := cmpmock.NewMockLogger(ctrl)

	svc := &BizDomainSvc{
		SvcBase: service.NewSvcBase(),
		logger:  mockLogger,
	}

	ctx := context.Background()
	agentTplIDs := []int64{1, 2, 3}
	dbErr := errors.New("database query failed")

	mockAgentTplRepo.EXPECT().GetAllIDs(gomock.Any()).Return(agentTplIDs, nil)
	mockBdAgentTplRelRepo.EXPECT().BeginTx(gomock.Any()).Return(nil, dbErr)

	resp, err := svc.FixMissingAgentTplRel(ctx, mockAgentTplRepo, mockBdAgentTplRelRepo)

	assert.Error(t, err)
	assert.Nil(t, resp)
}

func TestBizDomainSvc_FixMissingAgentTplRel_SingleAgent(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockAgentTplRepo := idbaccessmock.NewMockIDataAgentTplRepo(ctrl)
	mockBdAgentTplRelRepo := idbaccessmock.NewMockIBizDomainAgentTplRelRepo(ctrl)
	mockLogger := cmpmock.NewMockLogger(ctrl)

	svc := &BizDomainSvc{
		SvcBase: service.NewSvcBase(),
		logger:  mockLogger,
	}

	ctx := context.Background()
	agentTplIDs := []int64{1}
	txErr := errors.New("transaction error")

	mockAgentTplRepo.EXPECT().GetAllIDs(gomock.Any()).Return(agentTplIDs, nil)
	mockBdAgentTplRelRepo.EXPECT().BeginTx(gomock.Any()).Return(nil, txErr)

	resp, err := svc.FixMissingAgentTplRel(ctx, mockAgentTplRepo, mockBdAgentTplRelRepo)

	assert.Error(t, err)
	assert.Nil(t, resp)
}

func TestBizDomainSvc_FixMissingAgentTplRel_LargeNumberOfAgents(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockAgentTplRepo := idbaccessmock.NewMockIDataAgentTplRepo(ctrl)
	mockBdAgentTplRelRepo := idbaccessmock.NewMockIBizDomainAgentTplRelRepo(ctrl)
	mockLogger := cmpmock.NewMockLogger(ctrl)

	svc := &BizDomainSvc{
		SvcBase: service.NewSvcBase(),
		logger:  mockLogger,
	}

	ctx := context.Background()
	agentTplIDs := make([]int64, 100)
	for i := 0; i < 100; i++ {
		agentTplIDs[i] = int64(i + 1)
	}

	mockAgentTplRepo.EXPECT().GetAllIDs(gomock.Any()).Return(agentTplIDs, nil)
	mockBdAgentTplRelRepo.EXPECT().BeginTx(gomock.Any()).Return(nil, errors.New("tx error"))

	resp, err := svc.FixMissingAgentTplRel(ctx, mockAgentTplRepo, mockBdAgentTplRelRepo)

	assert.Error(t, err)
	assert.Nil(t, resp)
}

func TestBizDomainSvc_FixMissingAgentTplRel_TwoAgents(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockAgentTplRepo := idbaccessmock.NewMockIDataAgentTplRepo(ctrl)
	mockBdAgentTplRelRepo := idbaccessmock.NewMockIBizDomainAgentTplRelRepo(ctrl)
	mockLogger := cmpmock.NewMockLogger(ctrl)

	svc := &BizDomainSvc{
		SvcBase: service.NewSvcBase(),
		logger:  mockLogger,
	}

	ctx := context.Background()
	agentTplIDs := []int64{100, 200}
	txErr := errors.New("transaction begin failed")

	mockAgentTplRepo.EXPECT().GetAllIDs(gomock.Any()).Return(agentTplIDs, nil)
	mockBdAgentTplRelRepo.EXPECT().BeginTx(gomock.Any()).Return(nil, txErr)

	resp, err := svc.FixMissingAgentTplRel(ctx, mockAgentTplRepo, mockBdAgentTplRelRepo)

	assert.Error(t, err)
	assert.Nil(t, resp)
}

func TestBizDomainSvc_FixMissingAgentTplRel_MultipleAgents_BeginTxFails(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockAgentTplRepo := idbaccessmock.NewMockIDataAgentTplRepo(ctrl)
	mockBdAgentTplRelRepo := idbaccessmock.NewMockIBizDomainAgentTplRelRepo(ctrl)
	mockLogger := cmpmock.NewMockLogger(ctrl)

	svc := &BizDomainSvc{
		SvcBase: service.NewSvcBase(),
		logger:  mockLogger,
	}

	ctx := context.Background()
	agentTplIDs := []int64{1, 2, 3, 4, 5, 6, 7, 8, 9, 10}
	txErr := errors.New("transaction begin failed")

	mockAgentTplRepo.EXPECT().GetAllIDs(gomock.Any()).Return(agentTplIDs, nil)
	mockBdAgentTplRelRepo.EXPECT().BeginTx(gomock.Any()).Return(nil, txErr)

	resp, err := svc.FixMissingAgentTplRel(ctx, mockAgentTplRepo, mockBdAgentTplRelRepo)

	assert.Error(t, err)
	assert.Nil(t, resp)
}

func TestBizDomainSvc_FixMissingAgentTplRel_EmptyAgentList(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockAgentTplRepo := idbaccessmock.NewMockIDataAgentTplRepo(ctrl)
	mockBdAgentTplRelRepo := idbaccessmock.NewMockIBizDomainAgentTplRelRepo(ctrl)
	mockLogger := cmpmock.NewMockLogger(ctrl)

	svc := &BizDomainSvc{
		SvcBase: service.NewSvcBase(),
		logger:  mockLogger,
	}

	ctx := context.Background()
	agentTplIDs := []int64{}

	mockAgentTplRepo.EXPECT().GetAllIDs(gomock.Any()).Return(agentTplIDs, nil)
	mockLogger.EXPECT().Infoln(gomock.Any())

	resp, err := svc.FixMissingAgentTplRel(ctx, mockAgentTplRepo, mockBdAgentTplRelRepo)

	assert.NoError(t, err)
	assert.NotNil(t, resp)
	assert.Equal(t, 0, resp.FixedCount)
}
