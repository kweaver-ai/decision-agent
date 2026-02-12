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

func TestBizDomainSvc_InitBizDomainAgentRel_BeginTxError(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockAgentRepo := idbaccessmock.NewMockIDataAgentConfigRepo(ctrl)
	mockBdAgentRelRepo := idbaccessmock.NewMockIBizDomainAgentRelRepo(ctrl)
	mockLogger := cmpmock.NewMockLogger(ctrl)
	mockHttp := bizdomainaccmock.NewMockBizDomainHttpAcc(ctrl)

	svc := &BizDomainSvc{
		SvcBase:       service.NewSvcBase(),
		logger:        mockLogger,
		bizDomainHttp: mockHttp,
	}

	ctx := context.Background()
	txErr := errors.New("transaction begin failed")

	mockBdAgentRelRepo.EXPECT().BeginTx(gomock.Any()).Return(nil, txErr)

	err := svc.InitBizDomainAgentRel(ctx, mockAgentRepo, mockBdAgentRelRepo)

	assert.Error(t, err)
	assert.Contains(t, err.Error(), "begin tx failed")
}

// TestBizDomainSvc_InitBizDomainAgentRel_GetByBizDomainIDError tests error when getting existing relations fails
func TestBizDomainSvc_InitBizDomainAgentRel_GetByBizDomainIDError(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockAgentRepo := idbaccessmock.NewMockIDataAgentConfigRepo(ctrl)
	mockBdAgentRelRepo := idbaccessmock.NewMockIBizDomainAgentRelRepo(ctrl)
	mockLogger := cmpmock.NewMockLogger(ctrl)
	mockHttp := bizdomainaccmock.NewMockBizDomainHttpAcc(ctrl)

	svc := &BizDomainSvc{
		SvcBase:       service.NewSvcBase(),
		logger:        mockLogger,
		bizDomainHttp: mockHttp,
	}

	ctx := context.Background()
	mockTx := &sql.Tx{}
	dbErr := errors.New("database query failed")

	mockBdAgentRelRepo.EXPECT().BeginTx(gomock.Any()).Return(mockTx, nil)
	mockBdAgentRelRepo.EXPECT().GetByBizDomainID(ctx, mockTx, "bd_public").Return(nil, dbErr)

	err := svc.InitBizDomainAgentRel(ctx, mockAgentRepo, mockBdAgentRelRepo)

	assert.Error(t, err)
	assert.Contains(t, err.Error(), "get existing agent rels failed")
}

// TestBizDomainSvc_InitBizDomainAgentRel_GetAllIDsError tests error when getting all agent IDs fails
func TestBizDomainSvc_InitBizDomainAgentRel_GetAllIDsError(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockAgentRepo := idbaccessmock.NewMockIDataAgentConfigRepo(ctrl)
	mockBdAgentRelRepo := idbaccessmock.NewMockIBizDomainAgentRelRepo(ctrl)
	mockLogger := cmpmock.NewMockLogger(ctrl)
	mockHttp := bizdomainaccmock.NewMockBizDomainHttpAcc(ctrl)

	svc := &BizDomainSvc{
		SvcBase:       service.NewSvcBase(),
		logger:        mockLogger,
		bizDomainHttp: mockHttp,
	}

	ctx := context.Background()
	mockTx := &sql.Tx{}
	dbErr := errors.New("get all agent ids failed")

	mockBdAgentRelRepo.EXPECT().BeginTx(gomock.Any()).Return(mockTx, nil)
	mockBdAgentRelRepo.EXPECT().GetByBizDomainID(ctx, mockTx, "bd_public").Return([]*dapo.BizDomainAgentRelPo{}, nil)
	mockAgentRepo.EXPECT().GetAllIDs(ctx).Return(nil, dbErr)

	err := svc.InitBizDomainAgentRel(ctx, mockAgentRepo, mockBdAgentRelRepo)

	assert.Error(t, err)
	assert.Contains(t, err.Error(), "get all agent ids failed")
}

// TestBizDomainSvc_InitBizDomainAgentRel_SkipWhenExistingData tests skipping when data already exists
func TestBizDomainSvc_InitBizDomainAgentRel_SkipWhenExistingData(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockAgentRepo := idbaccessmock.NewMockIDataAgentConfigRepo(ctrl)
	mockBdAgentRelRepo := idbaccessmock.NewMockIBizDomainAgentRelRepo(ctrl)
	mockHttp := bizdomainaccmock.NewMockBizDomainHttpAcc(ctrl)

	svc := &BizDomainSvc{
		SvcBase:       service.NewSvcBase(),
		logger:        nil, // Set to nil to avoid panic in TxRollback with mock tx
		bizDomainHttp: mockHttp,
	}

	ctx := context.Background()
	mockTx := &sql.Tx{}

	// Setup expectations - return existing data
	existingRel := &dapo.BizDomainAgentRelPo{
		BizDomainID: "bd_public",
		AgentID:     "agent-1",
	}
	mockBdAgentRelRepo.EXPECT().BeginTx(gomock.Any()).Return(mockTx, nil)
	mockBdAgentRelRepo.EXPECT().GetByBizDomainID(ctx, mockTx, "bd_public").Return([]*dapo.BizDomainAgentRelPo{existingRel}, nil)

	err := svc.InitBizDomainAgentRel(ctx, mockAgentRepo, mockBdAgentRelRepo)

	// This should still return nil (success) when existing data is found
	assert.NoError(t, err)
}

// TestBizDomainSvc_InitBizDomainAgentRel_SkipWhenNoAgents tests skipping when no agents exist
func TestBizDomainSvc_InitBizDomainAgentRel_SkipWhenNoAgents(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockAgentRepo := idbaccessmock.NewMockIDataAgentConfigRepo(ctrl)
	mockBdAgentRelRepo := idbaccessmock.NewMockIBizDomainAgentRelRepo(ctrl)
	mockHttp := bizdomainaccmock.NewMockBizDomainHttpAcc(ctrl)

	svc := &BizDomainSvc{
		SvcBase:       service.NewSvcBase(),
		logger:        nil, // Set to nil to avoid panic in TxRollback with mock tx
		bizDomainHttp: mockHttp,
	}

	ctx := context.Background()
	mockTx := &sql.Tx{}

	// Setup expectations
	mockBdAgentRelRepo.EXPECT().BeginTx(gomock.Any()).Return(mockTx, nil)
	mockBdAgentRelRepo.EXPECT().GetByBizDomainID(ctx, mockTx, "bd_public").Return([]*dapo.BizDomainAgentRelPo{}, nil)
	mockAgentRepo.EXPECT().GetAllIDs(ctx).Return([]string{}, nil)

	err := svc.InitBizDomainAgentRel(ctx, mockAgentRepo, mockBdAgentRelRepo)

	assert.NoError(t, err)
}
