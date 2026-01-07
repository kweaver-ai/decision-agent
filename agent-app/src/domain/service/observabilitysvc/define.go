package observabilitysvc

import (
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/port/driven/ihttpaccess/iagentfactoryhttp"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/port/driven/ihttpaccess/iuniqueryhttp"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/port/driver/iportdriver"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-go-common-pkg/src/infra/cmp/icmp"
)

// NewObservabilitySvcDto 可观测性服务构造参数
type NewObservabilitySvcDto struct {
	Logger       icmp.Logger
	Uniquery     iuniqueryhttp.IUniquery
	AgentFactory iagentfactoryhttp.IAgentFactory
}

type observabilitySvc struct {
	logger       icmp.Logger
	uniquery     iuniqueryhttp.IUniquery
	agentFactory iagentfactoryhttp.IAgentFactory
}

var _ iportdriver.IObservability = &observabilitySvc{}

func NewObservabilitySvc(dto *NewObservabilitySvcDto) iportdriver.IObservability {
	return &observabilitySvc{
		logger:       dto.Logger,
		uniquery:     dto.Uniquery,
		agentFactory: dto.AgentFactory,
	}
}
