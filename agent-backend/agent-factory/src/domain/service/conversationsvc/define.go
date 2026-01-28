package conversationsvc

import (
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/service"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/cmp/icmp"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/idbaccess"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/ihttpaccess/iagentexecutorhttp"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/ihttpaccess/iagentfactoryhttp"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/ihttpaccess/iusermanagementacc"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/ihttpaccess/iv2agentexecutorhttp"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driver/iportdriver"
)

type conversationSvc struct {
	*service.SvcBase
	logger              icmp.Logger
	conversationRepo    idbaccess.IConversationRepo
	conversationMsgRepo idbaccess.IConversationMsgRepo
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
		agentExecutorV1:     dto.AgentExecutorV1,
		agentExecutorV2:     dto.AgentExecutorV2,
		agentFactory:        dto.AgentFactory,
	}

	return impl
}
