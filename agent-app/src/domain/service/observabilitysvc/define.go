package observabilitysvc

import (
	"github.com/kweaver-ai/decision-agent/agent-app/src/port/driven/ihttpaccess/iagentfactoryhttp"
	"github.com/kweaver-ai/decision-agent/agent-app/src/port/driven/ihttpaccess/iuniqueryhttp"
	"github.com/kweaver-ai/decision-agent/agent-app/src/port/driver/iportdriver"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/cmp/icmp"
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
