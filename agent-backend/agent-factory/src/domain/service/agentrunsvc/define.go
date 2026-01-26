package agentsvc

import (
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/service"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/cmp/icmp"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/idbaccess"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/ihttpaccess/iagentexecutorhttp"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/ihttpaccess/iagentfactoryhttp"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/ihttpaccess/idocsethttp"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/ihttpaccess/iefasthttp"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/ihttpaccess/iv2agentexecutorhttp"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driver/iportdriver"
)

type agentSvc struct {
	*service.SvcBase
	logger icmp.Logger
	// NOTE: 常量
	streamDiffFrequency int
	// NOTE: 注入一些其他服务
	agentFactory    iagentfactoryhttp.IAgentFactory
	agentExecutorV1 iagentexecutorhttp.IAgentExecutor
	agentExecutorV2 iv2agentexecutorhttp.IV2AgentExecutor
	efast           iefasthttp.IEfast
	conversationSvc iportdriver.IConversationSvc
	sessionSvc      iportdriver.ISessionSvc

	conversationRepo    idbaccess.IConversationRepo
	conversationMsgRepo idbaccess.IConversationMsgRepo
	tempAreaRepo        idbaccess.ITempAreaRepo
	docset              idocsethttp.IDocset
}

var _ iportdriver.IAgent = &agentSvc{}

type NewAgentSvcDto struct {
	SvcBase             *service.SvcBase
	Logger              icmp.Logger
	AgentFactory        iagentfactoryhttp.IAgentFactory
	AgentExecutorV1     iagentexecutorhttp.IAgentExecutor
	AgentExecutorV2     iv2agentexecutorhttp.IV2AgentExecutor
	Efast               iefasthttp.IEfast
	ConversationSvc     iportdriver.IConversationSvc
	SessionSvc          iportdriver.ISessionSvc
	ConversationRepo    idbaccess.IConversationRepo
	ConversationMsgRepo idbaccess.IConversationMsgRepo
	TempAreaRepo        idbaccess.ITempAreaRepo
	Docset              idocsethttp.IDocset
	StreamDiffFrequency int
}

func NewAgentSvc(dto *NewAgentSvcDto) iportdriver.IAgent {
	impl := &agentSvc{
		SvcBase:             dto.SvcBase,
		logger:              dto.Logger,
		agentFactory:        dto.AgentFactory,
		agentExecutorV1:     dto.AgentExecutorV1,
		agentExecutorV2:     dto.AgentExecutorV2,
		conversationSvc:     dto.ConversationSvc,
		sessionSvc:          dto.SessionSvc,
		conversationRepo:    dto.ConversationRepo,
		conversationMsgRepo: dto.ConversationMsgRepo,
		tempAreaRepo:        dto.TempAreaRepo,
		efast:               dto.Efast,
		docset:              dto.Docset,
		streamDiffFrequency: dto.StreamDiffFrequency,
	}

	return impl
}
