package permissionsvc

import (
	"testing"

	"go.uber.org/mock/gomock"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/service"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/idbaccess/idbaccessmock"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/ihttpaccess/iauthzacc/authzaccmock"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/ihttpaccess/iumacc/httpaccmock"
	"github.com/stretchr/testify/assert"
)

func TestNewPermissionService(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	dto := &NewPermissionSvcDto{
		SvcBase:               service.NewSvcBase(),
		AgentConfigRepo:       idbaccessmock.NewMockIDataAgentConfigRepo(ctrl),
		ReleaseRepo:           idbaccessmock.NewMockIReleaseRepo(ctrl),
		ReleasePermissionRepo: idbaccessmock.NewMockIReleasePermissionRepo(ctrl),
		UmHttp:                httpaccmock.NewMockUmHttpAcc(ctrl),
		AuthZHttp:             authzaccmock.NewMockAuthZHttpAcc(ctrl),
		SpaceRepo:             idbaccessmock.NewMockISpaceRepo(ctrl),
	}

	svc := NewPermissionService(dto)

	assert.NotNil(t, svc)
}
