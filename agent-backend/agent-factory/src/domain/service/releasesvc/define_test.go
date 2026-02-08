package releasesvc

import (
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/service"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/idbaccess/idbaccessmock"
	"github.com/stretchr/testify/assert"
	"go.uber.org/mock/gomock"
)

func TestNewReleaseService(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	dto := &NewReleaseSvcDto{
		SvcBase:                service.NewSvcBase(),
		ReleaseRepo:            idbaccessmock.NewMockIReleaseRepo(ctrl),
		ReleaseHistoryRepo:     idbaccessmock.NewMockIReleaseHistoryRepo(ctrl),
		AgentConfigRepo:        idbaccessmock.NewMockIDataAgentConfigRepo(ctrl),
		ReleaseCategoryRepo:    idbaccessmock.NewMockIReleaseCategoryRelRepo(ctrl),
		ReleasePermissionRepo:  idbaccessmock.NewMockIReleasePermissionRepo(ctrl),
		CategoryRepo:           idbaccessmock.NewMockICategoryRepo(ctrl),
		SpaceResourceRepo:      idbaccessmock.NewMockISpaceResourceRepo(ctrl),
	}

	svc := NewReleaseService(dto)

	assert.NotNil(t, svc)
}
