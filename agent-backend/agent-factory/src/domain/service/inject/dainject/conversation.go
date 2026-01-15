package dainject

import (
	"sync"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/service"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/service/conversationsvc"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/dbaccess/conversationdbacc"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/dbaccess/conversationmsgdbacc"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/dbaccess/tempareadbacc"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/httpaccess/httpinject"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driver/iportdriver"
	"github.com/kweaver-ai/kweaver-go-lib/logger"
)

var (
	conversationSvcOnce sync.Once
	conversationSvcImpl iportdriver.IConversationSvc
)

func NewConversationSvc() iportdriver.IConversationSvc {
	conversationSvcOnce.Do(func() {
		dto := &conversationsvc.NewConversationSvcDto{
			SvcBase:             service.NewSvcBase(),
			ConversationRepo:    conversationdbacc.NewConversationRepo(),
			ConversationMsgRepo: conversationmsgdbacc.NewConversationMsgRepo(),
			TempAreaRepo:        tempareadbacc.NewTempAreaRepo(),
			Logger:              logger.GetLogger(),
			AgentExecutorV1:     httpinject.NewAgentExecutorV1HttpAcc(),
			AgentExecutorV2:     httpinject.NewAgentExecutorV2HttpAcc(),
			AgentFactory:        httpinject.NewAgentFactoryHttpAcc(),
		}
		conversationSvcImpl = conversationsvc.NewConversationService(dto)
	})

	return conversationSvcImpl
}
