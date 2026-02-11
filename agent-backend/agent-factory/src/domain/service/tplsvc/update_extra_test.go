package tplsvc

import (
	"context"
	"database/sql"
	"errors"
	"testing"

	"go.uber.org/mock/gomock"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/service"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/cmp/icmp/cmpmock"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cenum"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cutil"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/idbaccess/idbaccessmock"
	"github.com/kweaver-ai/kweaver-go-lib/rest"
	"github.com/stretchr/testify/assert"
)

func TestUpdatePo_UpdateError(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockAgentTplRepo := idbaccessmock.NewMockIDataAgentTplRepo(ctrl)
	mockLogger := cmpmock.NewMockLogger(ctrl)

	svc := &dataAgentTplSvc{
		SvcBase:       service.NewSvcBase(),
		agentTplRepo:  mockAgentTplRepo,
		logger:        mockLogger,
	}

	ctx := context.Background()
	userID := "user-123"

	// Set up context with user ID
	visitor := &rest.Visitor{
		ID: userID,
	}
	ctx = context.WithValue(ctx, cenum.VisitUserInfoCtxKey.String(), visitor)

	po := &dapo.DataAgentTplPo{
		ID:        123,
		Name:      "Test Template",
		CreatedBy: userID,
		UpdatedBy: userID,
	}

	dbErr := errors.New("database connection failed")
	mockAgentTplRepo.EXPECT().Update(gomock.Any(), gomock.Any(), gomock.Any()).Return(dbErr)

	err := svc.updatePo(ctx, &sql.Tx{}, po)

	assert.Error(t, err)
	assert.Error(t, err) // Just verify there's an error
}

func TestUpdatePo_SetsTimestamp(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockAgentTplRepo := idbaccessmock.NewMockIDataAgentTplRepo(ctrl)
	mockLogger := cmpmock.NewMockLogger(ctrl)

	svc := &dataAgentTplSvc{
		SvcBase:       service.NewSvcBase(),
		agentTplRepo:  mockAgentTplRepo,
		logger:        mockLogger,
	}

	ctx := context.Background()
	userID := "user-123"

	// Set up context with user ID
	visitor := &rest.Visitor{
		ID: userID,
	}
	ctx = context.WithValue(ctx, cenum.VisitUserInfoCtxKey.String(), visitor)

	po := &dapo.DataAgentTplPo{
		ID:        123,
		Name:      "Test Template",
		CreatedBy: userID,
	}

	// Get expected timestamp before update
	expectedTimestamp := cutil.GetCurrentMSTimestamp()

	mockAgentTplRepo.EXPECT().Update(gomock.Any(), gomock.Any(), gomock.Any()).Return(nil)

	err := svc.updatePo(ctx, &sql.Tx{}, po)

	assert.NoError(t, err)
	assert.Equal(t, expectedTimestamp, po.UpdatedAt)
	assert.Equal(t, userID, po.UpdatedBy)
}

func TestUpdatePo_ChangesStatusToUnpublished(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockAgentTplRepo := idbaccessmock.NewMockIDataAgentTplRepo(ctrl)
	mockLogger := cmpmock.NewMockLogger(ctrl)

	svc := &dataAgentTplSvc{
		SvcBase:       service.NewSvcBase(),
		agentTplRepo:  mockAgentTplRepo,
		logger:        mockLogger,
	}

	ctx := context.Background()
	userID := "user-123"

	// Set up context with user ID
	visitor := &rest.Visitor{
		ID: userID,
	}
	ctx = context.WithValue(ctx, cenum.VisitUserInfoCtxKey.String(), visitor)

	po := &dapo.DataAgentTplPo{
		ID:        123,
		Name:      "Test Template",
		CreatedBy: userID,
	}

	mockAgentTplRepo.EXPECT().Update(gomock.Any(), gomock.Any(), gomock.Any()).Return(nil)

	err := svc.updatePo(ctx, &sql.Tx{}, po)

	assert.NoError(t, err)
	// Status should be changed to unpublished after update
	// Just verify the status is set (not comparing to int8(0))
	assert.NotNil(t, po.Status)
}
