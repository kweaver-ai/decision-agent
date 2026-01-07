package dainject

import (
	"sync"

	"github.com/kweaver-ai/decision-agent/agent-app/src/domain/service"
	"github.com/kweaver-ai/decision-agent/agent-app/src/domain/service/agentsvc"
	"github.com/kweaver-ai/decision-agent/agent-app/src/drivenadapter/dbaccess/conversationdbacc"
	"github.com/kweaver-ai/decision-agent/agent-app/src/drivenadapter/dbaccess/conversationmsgdbacc"
	"github.com/kweaver-ai/decision-agent/agent-app/src/drivenadapter/dbaccess/tempareadbacc"
	"github.com/kweaver-ai/decision-agent/agent-app/src/drivenadapter/httpaccess/httpinject"
	"github.com/kweaver-ai/decision-agent/agent-app/src/infra/common/global"
	"github.com/kweaver-ai/decision-agent/agent-app/src/port/driver/iportdriver"
	"github.com/kweaver-ai/kweaver-go-lib/logger"
)

var (
	agentSvcOnce sync.Once
	agentSvcImpl iportdriver.IAgent
)

func NewAgentSvc() iportdriver.IAgent {
	agentSvcOnce.Do(func() {
		dto := &agentsvc.NewAgentSvcDto{
			SvcBase:             service.NewSvcBase(),
			Logger:              logger.GetLogger(),
			AgentFactory:        httpinject.NewAgentFactoryHttpAcc(),
			AgentExecutorV1:     httpinject.NewAgentExecutorV1HttpAcc(),
			AgentExecutorV2:     httpinject.NewAgentExecutorV2HttpAcc(),
			ConversationSvc:     NewConversationSvc(),
			SessionSvc:          NewSessionSvc(),
			ConversationRepo:    conversationdbacc.NewConversationRepo(),
			ConversationMsgRepo: conversationmsgdbacc.NewConversationMsgRepo(),
			Efast:               httpinject.NewEfastHttpAcc(),

			Text2Vec:     agentsvc.NewText2Vec(),
			TempAreaRepo: tempareadbacc.NewTempAreaRepo(),
			Docset:       httpinject.NewDocsetHttpAcc(),
			// NOTE: streamDiffFrequency must be greater than 0
			StreamDiffFrequency: max(global.GConfig.StreamDiffFrequency, 1),
		}

		agentSvcImpl = agentsvc.NewAgentSvc(dto)
	})

	return agentSvcImpl
}
