package personalspacesvc

import (
	"testing"

	"go.uber.org/mock/gomock"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/service"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/idbaccess/idbaccessmock"
	"github.com/stretchr/testify/assert"
)

func TestNewPersonalSpaceService(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	dto := &NewPersonalSpaceSvcDto{
		SvcBase:           service.NewSvcBase(),
		AgentTplRepo:      idbaccessmock.NewMockIDataAgentTplRepo(ctrl),
		AgentConfigRepo:   idbaccessmock.NewMockIDataAgentConfigRepo(ctrl),
		PersonalSpaceRepo: idbaccessmock.NewMockIPersonalSpaceRepo(ctrl),
		ReleaseRepo:       idbaccessmock.NewMockIReleaseRepo(ctrl),
		PubedAgentRepo:    idbaccessmock.NewMockIPubedAgentRepo(ctrl),
	}

	svc := NewPersonalSpaceService(dto)

	assert.NotNil(t, svc)
}
