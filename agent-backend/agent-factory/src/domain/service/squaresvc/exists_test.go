package squaresvc

import (
	"context"
	"errors"
	"testing"

	"github.com/stretchr/testify/assert"
	"go.uber.org/mock/gomock"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/idbaccess/idbaccessmock"
)

func TestIsAgentExists(t *testing.T) {
	t.Parallel()

	t.Run("agent exists", func(t *testing.T) {
		t.Parallel()

		ctrl := gomock.NewController(t)
		defer ctrl.Finish()

		mockRepo := idbaccessmock.NewMockIDataAgentConfigRepo(ctrl)
		mockRepo.EXPECT().ExistsByID(gomock.Any(), "agent-123").Return(true, nil)

		svc := &squareSvc{
			agentConfRepo: mockRepo,
		}

		exists, err := svc.IsAgentExists(context.Background(), "agent-123")

		assert.True(t, exists)
		assert.NoError(t, err)
	})

	t.Run("agent does not exist", func(t *testing.T) {
		t.Parallel()

		ctrl := gomock.NewController(t)
		defer ctrl.Finish()

		mockRepo := idbaccessmock.NewMockIDataAgentConfigRepo(ctrl)
		mockRepo.EXPECT().ExistsByID(gomock.Any(), "agent-456").Return(false, nil)

		svc := &squareSvc{
			agentConfRepo: mockRepo,
		}

		exists, err := svc.IsAgentExists(context.Background(), "agent-456")

		assert.False(t, exists)
		assert.NoError(t, err)
	})

	t.Run("repository error", func(t *testing.T) {
		t.Parallel()

		ctrl := gomock.NewController(t)
		defer ctrl.Finish()

		mockRepo := idbaccessmock.NewMockIDataAgentConfigRepo(ctrl)
		expectedErr := errors.New("database error")
		mockRepo.EXPECT().ExistsByID(gomock.Any(), "agent-789").Return(false, expectedErr)

		svc := &squareSvc{
			agentConfRepo: mockRepo,
		}

		exists, err := svc.IsAgentExists(context.Background(), "agent-789")

		assert.False(t, exists)
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "[squareSvc.IsAgentExists]")
	})
}

func TestIsSpaceExists(t *testing.T) {
	t.Parallel()

	t.Run("space exists", func(t *testing.T) {
		t.Parallel()

		ctrl := gomock.NewController(t)
		defer ctrl.Finish()

		mockRepo := idbaccessmock.NewMockISpaceRepo(ctrl)
		mockRepo.EXPECT().ExistsByID(gomock.Any(), "space-123").Return(true, nil)

		svc := &squareSvc{
			spaceRepo: mockRepo,
		}

		exists, err := svc.IsSpaceExists(context.Background(), "space-123")

		assert.True(t, exists)
		assert.NoError(t, err)
	})

	t.Run("space does not exist", func(t *testing.T) {
		t.Parallel()

		ctrl := gomock.NewController(t)
		defer ctrl.Finish()

		mockRepo := idbaccessmock.NewMockISpaceRepo(ctrl)
		mockRepo.EXPECT().ExistsByID(gomock.Any(), "space-456").Return(false, nil)

		svc := &squareSvc{
			spaceRepo: mockRepo,
		}

		exists, err := svc.IsSpaceExists(context.Background(), "space-456")

		assert.False(t, exists)
		assert.NoError(t, err)
	})

	t.Run("repository error", func(t *testing.T) {
		t.Parallel()

		ctrl := gomock.NewController(t)
		defer ctrl.Finish()

		mockRepo := idbaccessmock.NewMockISpaceRepo(ctrl)
		expectedErr := errors.New("database error")
		mockRepo.EXPECT().ExistsByID(gomock.Any(), "space-789").Return(false, expectedErr)

		svc := &squareSvc{
			spaceRepo: mockRepo,
		}

		exists, err := svc.IsSpaceExists(context.Background(), "space-789")

		assert.False(t, exists)
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "[squareSvc.IsSpaceExists]")
	})
}
