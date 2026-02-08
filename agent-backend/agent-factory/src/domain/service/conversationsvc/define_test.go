package conversationsvc

import (
	"testing"

	"go.uber.org/mock/gomock"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/service"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/idbaccess/idbaccessmock"
	"github.com/stretchr/testify/assert"
)

func TestNewConversationService(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	dto := &NewConversationSvcDto{
		SvcBase:             service.NewSvcBase(),
		ConversationRepo:    idbaccessmock.NewMockIConversationRepo(ctrl),
		ConversationMsgRepo: idbaccessmock.NewMockIConversationMsgRepo(ctrl),
		Logger:              nil,
		OpenAICmp:           nil,
		UmHttp:              nil,
		AgentExecutorV1:     nil,
		AgentExecutorV2:     nil,
		AgentFactory:        nil,
		SandboxPlatform:     nil,
		SandboxPlatformConf: nil,
	}

	svc := NewConversationService(dto)

	assert.NotNil(t, svc)
}
