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

func TestBizDomainSvc_InitBizDomainAgentTplRel_BeginTxError(t *testing.T) {
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
	txErr := errors.New("transaction begin failed")

	mockBdAgentTplRelRepo.EXPECT().BeginTx(gomock.Any()).Return(nil, txErr)

	err := svc.InitBizDomainAgentTplRel(ctx, mockAgentTplRepo, mockBdAgentTplRelRepo)

	assert.Error(t, err)
	assert.Contains(t, err.Error(), "begin tx failed")
}

// TestBizDomainSvc_InitBizDomainAgentTplRel_GetByBizDomainIDError tests error when getting existing relations fails
func TestBizDomainSvc_InitBizDomainAgentTplRel_GetByBizDomainIDError(t *testing.T) {
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
	mockTx := &sql.Tx{}
	dbErr := errors.New("database query failed")

	mockBdAgentTplRelRepo.EXPECT().BeginTx(gomock.Any()).Return(mockTx, nil)
	mockBdAgentTplRelRepo.EXPECT().GetByBizDomainID(ctx, mockTx, "public").Return(nil, dbErr)

	err := svc.InitBizDomainAgentTplRel(ctx, mockAgentTplRepo, mockBdAgentTplRelRepo)

	assert.Error(t, err)
	assert.Contains(t, err.Error(), "get existing agent tpl rels failed")
}

// TestBizDomainSvc_InitBizDomainAgentTplRel_GetAllIDsError tests error when getting all agent template IDs fails
func TestBizDomainSvc_InitBizDomainAgentTplRel_GetAllIDsError(t *testing.T) {
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
	mockTx := &sql.Tx{}
	dbErr := errors.New("get all agent tpl ids failed")

	mockBdAgentTplRelRepo.EXPECT().BeginTx(gomock.Any()).Return(mockTx, nil)
	mockBdAgentTplRelRepo.EXPECT().GetByBizDomainID(ctx, mockTx, "public").Return([]*dapo.BizDomainAgentTplRelPo{}, nil)
	mockAgentTplRepo.EXPECT().GetAllIDs(ctx).Return(nil, dbErr)

	err := svc.InitBizDomainAgentTplRel(ctx, mockAgentTplRepo, mockBdAgentTplRelRepo)

	assert.Error(t, err)
	assert.Contains(t, err.Error(), "get all agent tpl ids failed")
}

// TestBizDomainSvc_InitBizDomainAgentTplRel_SkipWhenExistingData tests skipping when data already exists
func TestBizDomainSvc_InitBizDomainAgentTplRel_SkipWhenExistingData(t *testing.T) {
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
	mockTx := &sql.Tx{}

	// Setup expectations - return existing data
	existingRel := &dapo.BizDomainAgentTplRelPo{
		BizDomainID: "public",
		AgentTplID:  1,
	}
	mockBdAgentTplRelRepo.EXPECT().BeginTx(gomock.Any()).Return(mockTx, nil)
	mockBdAgentTplRelRepo.EXPECT().GetByBizDomainID(ctx, mockTx, "public").Return([]*dapo.BizDomainAgentTplRelPo{existingRel}, nil)
	mockLogger.EXPECT().Infof(gomock.Any(), gomock.Any())

	err := svc.InitBizDomainAgentTplRel(ctx, mockAgentTplRepo, mockBdAgentTplRelRepo)

	assert.NoError(t, err)
}

// TestBizDomainSvc_InitBizDomainAgentTplRel_SkipWhenNoAgentTpls tests skipping when no agent templates exist
func TestBizDomainSvc_InitBizDomainAgentTplRel_SkipWhenNoAgentTpls(t *testing.T) {
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
	mockTx := &sql.Tx{}

	// Setup expectations
	mockBdAgentTplRelRepo.EXPECT().BeginTx(gomock.Any()).Return(mockTx, nil)
	mockBdAgentTplRelRepo.EXPECT().GetByBizDomainID(ctx, mockTx, "public").Return([]*dapo.BizDomainAgentTplRelPo{}, nil)
	mockAgentTplRepo.EXPECT().GetAllIDs(ctx).Return([]int64{}, nil)
	mockLogger.EXPECT().Infoln(gomock.Any())

	err := svc.InitBizDomainAgentTplRel(ctx, mockAgentTplRepo, mockBdAgentTplRelRepo)

	assert.NoError(t, err)
}
