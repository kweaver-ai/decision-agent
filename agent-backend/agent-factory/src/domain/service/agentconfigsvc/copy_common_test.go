package v3agentconfigsvc

import (
	"context"
	"database/sql"
	"errors"
	"testing"

	"go.uber.org/mock/gomock"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/service"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/idbaccess/idbaccessmock"
	"github.com/stretchr/testify/assert"
)

func TestGetPublishedAgentPo(t *testing.T) {
	t.Run("returns error when repo fails", func(t *testing.T) {
		ctrl := gomock.NewController(t)
		defer ctrl.Finish()

		mockRepo := idbaccessmock.NewMockIPubedAgentRepo(ctrl)
		svc := &dataAgentConfigSvc{
			SvcBase:        service.NewSvcBase(),
			pubedAgentRepo: mockRepo,
		}

		ctx := context.Background()
		mockRepo.EXPECT().GetPubedPoMapByXx(gomock.Any(), gomock.Any()).Return(nil, errors.New("repo error"))

		po, err := svc.getPublishedAgentPo(ctx, "agent1")

		assert.Error(t, err)
		assert.Nil(t, po)
	})

	t.Run("returns error when agent not found in result", func(t *testing.T) {
		t.Skip("Requires proper mock return type structure")
	})
}

func TestGetAgentPoForCopy(t *testing.T) {
	t.Run("returns error when repo not found", func(t *testing.T) {
		ctrl := gomock.NewController(t)
		defer ctrl.Finish()

		mockRepo := idbaccessmock.NewMockIDataAgentConfigRepo(ctrl)
		svc := &dataAgentConfigSvc{
			SvcBase:      service.NewSvcBase(),
			agentConfRepo: mockRepo,
		}

		ctx := context.Background()
		mockRepo.EXPECT().GetByID(ctx, "agent1").Return(nil, sql.ErrNoRows)

		po, err := svc.getAgentPoForCopy(ctx, "agent1")

		assert.Error(t, err)
		assert.Nil(t, po)
	})

	t.Run("returns agent po when found", func(t *testing.T) {
		ctrl := gomock.NewController(t)
		defer ctrl.Finish()

		mockRepo := idbaccessmock.NewMockIDataAgentConfigRepo(ctrl)
		svc := &dataAgentConfigSvc{
			SvcBase:      service.NewSvcBase(),
			agentConfRepo: mockRepo,
		}

		ctx := context.Background()
		expectedPo := &dapo.DataAgentPo{
			ID: "agent1",
		}
		mockRepo.EXPECT().GetByID(ctx, "agent1").Return(expectedPo, nil)

		po, err := svc.getAgentPoForCopy(ctx, "agent1")

		assert.NoError(t, err)
		assert.Equal(t, expectedPo, po)
	})
}
