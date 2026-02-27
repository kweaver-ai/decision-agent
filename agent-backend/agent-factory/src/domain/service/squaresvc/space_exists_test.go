package squaresvc

import (
	"context"
	"errors"
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/service"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/idbaccess/idbaccessmock"
	"github.com/stretchr/testify/assert"
	"go.uber.org/mock/gomock"
)

func TestSquareSvc_IsSpaceExists_Exists(t *testing.T) {
	t.Parallel()

	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockSpaceRepo := idbaccessmock.NewMockISpaceRepo(ctrl)

	svc := &squareSvc{
		SvcBase:   service.NewSvcBase(),
		spaceRepo: mockSpaceRepo,
	}

	ctx := context.Background()
	spaceID := "space-123"

	mockSpaceRepo.EXPECT().ExistsByID(gomock.Any(), spaceID).Return(true, nil)

	exists, err := svc.IsSpaceExists(ctx, spaceID)

	assert.NoError(t, err)
	assert.True(t, exists)
}

func TestSquareSvc_IsSpaceExists_NotExists(t *testing.T) {
	t.Parallel()

	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockSpaceRepo := idbaccessmock.NewMockISpaceRepo(ctrl)

	svc := &squareSvc{
		SvcBase:   service.NewSvcBase(),
		spaceRepo: mockSpaceRepo,
	}

	ctx := context.Background()
	spaceID := "space-999"

	mockSpaceRepo.EXPECT().ExistsByID(gomock.Any(), spaceID).Return(false, nil)

	exists, err := svc.IsSpaceExists(ctx, spaceID)

	assert.NoError(t, err)
	assert.False(t, exists)
}

func TestSquareSvc_IsSpaceExists_RepoError(t *testing.T) {
	t.Parallel()

	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockSpaceRepo := idbaccessmock.NewMockISpaceRepo(ctrl)

	svc := &squareSvc{
		SvcBase:   service.NewSvcBase(),
		spaceRepo: mockSpaceRepo,
	}

	ctx := context.Background()
	spaceID := "space-123"
	dbErr := errors.New("database connection failed")

	mockSpaceRepo.EXPECT().ExistsByID(gomock.Any(), spaceID).Return(false, dbErr)

	exists, err := svc.IsSpaceExists(ctx, spaceID)

	assert.Error(t, err)
	assert.False(t, exists)
	assert.Contains(t, err.Error(), "IsSpaceExists")
}
