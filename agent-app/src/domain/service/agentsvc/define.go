package agentsvc

import (
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/domain/service"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/port/driven/idbaccess"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/port/driven/ihttpaccess/iagentexecutorhttp"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/port/driven/ihttpaccess/iagentfactoryhttp"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/port/driven/ihttpaccess/idocsethttp"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/port/driven/ihttpaccess/iefasthttp"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/port/driven/ihttpaccess/iv2agentexecutorhttp"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/port/driver/iportdriver"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-go-common-pkg/src/infra/cmp/icmp"
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
	Text2Vec            *text2Vec
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
	Text2Vec            *text2Vec
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
		Text2Vec:            dto.Text2Vec,
		docset:              dto.Docset,
		streamDiffFrequency: dto.StreamDiffFrequency,
	}

	return impl
}
