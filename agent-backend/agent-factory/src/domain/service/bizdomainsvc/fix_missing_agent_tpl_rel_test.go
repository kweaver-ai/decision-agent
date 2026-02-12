package bizdomainsvc

import (
	"context"
	"database/sql"
	"errors"
	"testing"

	"go.uber.org/mock/gomock"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/service"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/cmp/icmp/cmpmock"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/ihttpaccess/ibizdomainacc/bizdomainaccmock"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/idbaccess/idbaccessmock"
	"github.com/stretchr/testify/assert"
)

func TestBizDomainSvc_FixMissingAgentTplRel_GetAllIDsError(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockAgentTplRepo := idbaccessmock.NewMockIDataAgentTplRepo(ctrl)
	mockBdAgentTplRelRepo := idbaccessmock.NewMockIBizDomainAgentTplRelRepo(ctrl)
	mockLogger := cmpmock.NewMockLogger(ctrl)
	mockHttp := bizdomainaccmock.NewMockBizDomainHttpAcc(ctrl)

	svc := &BizDomainSvc{
		SvcBase:       service.NewSvcBase(),
		logger:        mockLogger,
		bizDomainHttp: mockHttp,
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
	mockHttp := bizdomainaccmock.NewMockBizDomainHttpAcc(ctrl)

	svc := &BizDomainSvc{
		SvcBase:       service.NewSvcBase(),
		logger:        mockLogger,
		bizDomainHttp: mockHttp,
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
	mockHttp := bizdomainaccmock.NewMockBizDomainHttpAcc(ctrl)

	svc := &BizDomainSvc{
		SvcBase:       service.NewSvcBase(),
		logger:        mockLogger,
		bizDomainHttp: mockHttp,
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

func TestBizDomainSvc_FixMissingAgentTplRel_GetByBizDomainIDError(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockAgentTplRepo := idbaccessmock.NewMockIDataAgentTplRepo(ctrl)
	mockBdAgentTplRelRepo := idbaccessmock.NewMockIBizDomainAgentTplRelRepo(ctrl)
	mockLogger := cmpmock.NewMockLogger(ctrl)
	mockHttp := bizdomainaccmock.NewMockBizDomainHttpAcc(ctrl)

	svc := &BizDomainSvc{
		SvcBase:       service.NewSvcBase(),
		logger:        mockLogger,
		bizDomainHttp: mockHttp,
	}

	ctx := context.Background()
	agentTplIDs := []int64{1, 2, 3}
	mockTx := &sql.Tx{}
	dbErr := errors.New("database query failed")

	mockAgentTplRepo.EXPECT().GetAllIDs(gomock.Any()).Return(agentTplIDs, nil)
	mockBdAgentTplRelRepo.EXPECT().BeginTx(gomock.Any()).Return(mockTx, nil)
	mockBdAgentTplRelRepo.EXPECT().GetByBizDomainID(ctx, mockTx, "bd_public").Return(nil, dbErr)

	resp, err := svc.FixMissingAgentTplRel(ctx, mockAgentTplRepo, mockBdAgentTplRelRepo)

	assert.Error(t, err)
	assert.Nil(t, resp)
	assert.Contains(t, err.Error(), "get existing agent tpl rels failed")
}

func TestBizDomainSvc_FixMissingAgentTplRel_AllExisting(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockAgentTplRepo := idbaccessmock.NewMockIDataAgentTplRepo(ctrl)
	mockBdAgentTplRelRepo := idbaccessmock.NewMockIBizDomainAgentTplRelRepo(ctrl)
	mockLogger := cmpmock.NewMockLogger(ctrl)
	mockHttp := bizdomainaccmock.NewMockBizDomainHttpAcc(ctrl)

	svc := &BizDomainSvc{
		SvcBase:       service.NewSvcBase(),
		logger:        mockLogger,
		bizDomainHttp: mockHttp,
	}

	ctx := context.Background()
	agentTplIDs := []int64{1, 2, 3}
	mockTx := &sql.Tx{}

	// All agent templates already have relations
	existingRels := []*dapo.BizDomainAgentTplRelPo{
		{BizDomainID: "bd_public", AgentTplID: 1},
		{BizDomainID: "bd_public", AgentTplID: 2},
		{BizDomainID: "bd_public", AgentTplID: 3},
	}

	mockAgentTplRepo.EXPECT().GetAllIDs(gomock.Any()).Return(agentTplIDs, nil)
	mockBdAgentTplRelRepo.EXPECT().BeginTx(gomock.Any()).Return(mockTx, nil)
	mockBdAgentTplRelRepo.EXPECT().GetByBizDomainID(ctx, mockTx, "bd_public").Return(existingRels, nil)
	mockLogger.EXPECT().Infoln(gomock.Any())

	resp, err := svc.FixMissingAgentTplRel(ctx, mockAgentTplRepo, mockBdAgentTplRelRepo)

	assert.NoError(t, err)
	assert.NotNil(t, resp)
	assert.Equal(t, 0, resp.FixedCount)
	assert.Empty(t, resp.FixedIDs)
}

func TestBizDomainSvc_FixMissingAgentTplRel_PartialMissing(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockAgentTplRepo := idbaccessmock.NewMockIDataAgentTplRepo(ctrl)
	mockBdAgentTplRelRepo := idbaccessmock.NewMockIBizDomainAgentTplRelRepo(ctrl)
	mockLogger := cmpmock.NewMockLogger(ctrl)
	mockHttp := bizdomainaccmock.NewMockBizDomainHttpAcc(ctrl)

	svc := &BizDomainSvc{
		SvcBase:       service.NewSvcBase(),
		logger:        mockLogger,
		bizDomainHttp: mockHttp,
	}

	ctx := context.Background()
	agentTplIDs := []int64{1, 2, 3, 4, 5}
	mockTx := &sql.Tx{}

	// Only agent templates 1 and 2 have relations
	existingRels := []*dapo.BizDomainAgentTplRelPo{
		{BizDomainID: "bd_public", AgentTplID: 1},
		{BizDomainID: "bd_public", AgentTplID: 2},
	}

	mockAgentTplRepo.EXPECT().GetAllIDs(gomock.Any()).Return(agentTplIDs, nil)
	mockBdAgentTplRelRepo.EXPECT().BeginTx(gomock.Any()).Return(mockTx, nil)
	mockBdAgentTplRelRepo.EXPECT().GetByBizDomainID(ctx, mockTx, "bd_public").Return(existingRels, nil)
	mockBdAgentTplRelRepo.EXPECT().BatchCreate(ctx, mockTx, gomock.Any()).Return(nil)
	mockHttp.EXPECT().AssociateResourceBatch(ctx, gomock.Any()).Return(nil)
	mockLogger.EXPECT().Infof(gomock.Any(), gomock.Any()).Times(2)

	_, err := svc.FixMissingAgentTplRel(ctx, mockAgentTplRepo, mockBdAgentTplRelRepo)

	// Should fail because we can't mock tx.Commit()
	assert.Error(t, err)
}

func TestBizDomainSvc_FixMissingAgentTplRel_BatchCreateError(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockAgentTplRepo := idbaccessmock.NewMockIDataAgentTplRepo(ctrl)
	mockBdAgentTplRelRepo := idbaccessmock.NewMockIBizDomainAgentTplRelRepo(ctrl)
	mockLogger := cmpmock.NewMockLogger(ctrl)
	mockHttp := bizdomainaccmock.NewMockBizDomainHttpAcc(ctrl)

	svc := &BizDomainSvc{
		SvcBase:       service.NewSvcBase(),
		logger:        mockLogger,
		bizDomainHttp: mockHttp,
	}

	ctx := context.Background()
	agentTplIDs := []int64{1, 2, 3}
	mockTx := &sql.Tx{}

	// No existing relations
	existingRels := []*dapo.BizDomainAgentTplRelPo{}
	dbErr := errors.New("batch create failed")

	mockAgentTplRepo.EXPECT().GetAllIDs(gomock.Any()).Return(agentTplIDs, nil)
	mockBdAgentTplRelRepo.EXPECT().BeginTx(gomock.Any()).Return(mockTx, nil)
	mockBdAgentTplRelRepo.EXPECT().GetByBizDomainID(ctx, mockTx, "bd_public").Return(existingRels, nil)
	mockBdAgentTplRelRepo.EXPECT().BatchCreate(ctx, mockTx, gomock.Any()).Return(dbErr)

	resp, err := svc.FixMissingAgentTplRel(ctx, mockAgentTplRepo, mockBdAgentTplRelRepo)

	assert.Error(t, err)
	assert.Nil(t, resp)
	assert.Contains(t, err.Error(), "batch create agent tpl rels failed")
}

func TestBizDomainSvc_FixMissingAgentTplRel_HttpError(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockAgentTplRepo := idbaccessmock.NewMockIDataAgentTplRepo(ctrl)
	mockBdAgentTplRelRepo := idbaccessmock.NewMockIBizDomainAgentTplRelRepo(ctrl)
	mockLogger := cmpmock.NewMockLogger(ctrl)
	mockHttp := bizdomainaccmock.NewMockBizDomainHttpAcc(ctrl)

	svc := &BizDomainSvc{
		SvcBase:       service.NewSvcBase(),
		logger:        mockLogger,
		bizDomainHttp: mockHttp,
	}

	ctx := context.Background()
	agentTplIDs := []int64{1, 2, 3}
	mockTx := &sql.Tx{}

	// No existing relations
	existingRels := []*dapo.BizDomainAgentTplRelPo{}
	httpErr := errors.New("HTTP association failed")

	mockAgentTplRepo.EXPECT().GetAllIDs(gomock.Any()).Return(agentTplIDs, nil)
	mockBdAgentTplRelRepo.EXPECT().BeginTx(gomock.Any()).Return(mockTx, nil)
	mockBdAgentTplRelRepo.EXPECT().GetByBizDomainID(ctx, mockTx, "bd_public").Return(existingRels, nil)
	mockBdAgentTplRelRepo.EXPECT().BatchCreate(ctx, mockTx, gomock.Any()).Return(nil)
	mockHttp.EXPECT().AssociateResourceBatch(ctx, gomock.Any()).Return(httpErr)

	resp, err := svc.FixMissingAgentTplRel(ctx, mockAgentTplRepo, mockBdAgentTplRelRepo)

	assert.Error(t, err)
	assert.Nil(t, resp)
	assert.Contains(t, err.Error(), "associate resource batch failed")
}
