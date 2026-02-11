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

func TestBizDomainSvc_InitBizDomainAgentTplRel_BeginTxError(t *testing.T) {
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
	txErr := errors.New("transaction begin failed")

	mockBdAgentTplRelRepo.EXPECT().BeginTx(gomock.Any()).Return(nil, txErr)

	err := svc.InitBizDomainAgentTplRel(ctx, mockAgentTplRepo, mockBdAgentTplRelRepo)

	assert.Error(t, err)
	assert.Contains(t, err.Error(), "begin tx failed")
}

func TestBizDomainSvc_InitBizDomainAgentTplRel_GetByBizDomainIDError(t *testing.T) {
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

	mockBdAgentTplRelRepo.EXPECT().BeginTx(gomock.Any()).Return(nil, dbErr)

	err := svc.InitBizDomainAgentTplRel(ctx, mockAgentTplRepo, mockBdAgentTplRelRepo)

	assert.Error(t, err)
}

func TestBizDomainSvc_InitBizDomainAgentTplRel_GetAllIDsError(t *testing.T) {
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

	mockBdAgentTplRelRepo.EXPECT().BeginTx(gomock.Any()).Return(nil, dbErr)

	err := svc.InitBizDomainAgentTplRel(ctx, mockAgentTplRepo, mockBdAgentTplRelRepo)

	assert.Error(t, err)
}
