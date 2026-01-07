package conversationsvc

import (
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/domain/service"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/port/driven/idbaccess"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/port/driven/ihttpaccess/iagentexecutorhttp"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/port/driven/ihttpaccess/iagentfactoryhttp"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/port/driven/ihttpaccess/iv2agentexecutorhttp"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/port/driver/iportdriver"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-go-common-pkg/src/infra/cmp/icmp"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-go-common-pkg/src/port/driven/ihttpaccess/iusermanagementacc"
)

type conversationSvc struct {
	*service.SvcBase
	logger              icmp.Logger
	conversationRepo    idbaccess.IConversationRepo
	conversationMsgRepo idbaccess.IConversationMsgRepo
	tempAreaRepo        idbaccess.ITempAreaRepo
	agentExecutorV1     iagentexecutorhttp.IAgentExecutor
	agentExecutorV2     iv2agentexecutorhttp.IV2AgentExecutor
	agentFactory        iagentfactoryhttp.IAgentFactory
}

var _ iportdriver.IConversationSvc = &conversationSvc{}

type NewConversationSvcDto struct {
	SvcBase             *service.SvcBase
	ConversationRepo    idbaccess.IConversationRepo
	ConversationMsgRepo idbaccess.IConversationMsgRepo
	Logger              icmp.Logger
	OpenAICmp           icmp.IOpenAI
	UmHttp              iusermanagementacc.UserMgnt
	TempAreaRepo        idbaccess.ITempAreaRepo
	AgentExecutorV1     iagentexecutorhttp.IAgentExecutor
	AgentExecutorV2     iv2agentexecutorhttp.IV2AgentExecutor
	AgentFactory        iagentfactoryhttp.IAgentFactory
}

func NewConversationService(dto *NewConversationSvcDto) iportdriver.IConversationSvc {
	impl := &conversationSvc{
		SvcBase:             dto.SvcBase,
		conversationRepo:    dto.ConversationRepo,
		conversationMsgRepo: dto.ConversationMsgRepo,
		logger:              dto.Logger,
		tempAreaRepo:        dto.TempAreaRepo,
		agentExecutorV1:     dto.AgentExecutorV1,
		agentExecutorV2:     dto.AgentExecutorV2,
		agentFactory:        dto.AgentFactory,
	}

	return impl
}
