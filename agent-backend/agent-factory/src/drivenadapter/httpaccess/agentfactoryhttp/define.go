package agentfactoryhttp

import (
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/cmp/icmp"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cglobal"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cutil"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/ihttpaccess/iagentfactoryacc"
)

type agentFactoryHttpAcc struct {
	logger         icmp.Logger
	privateBaseURL string
}

var _ iagentfactoryacc.IAgentFactoryHttpAcc = &agentFactoryHttpAcc{}

func NewAgentFactoryHttpAcc(
	_logger icmp.Logger,
) iagentfactoryacc.IAgentFactoryHttpAcc {
	// 从配置中获取授权服务的地址
	agentFactoryConf := cglobal.GConfig.AgentFactory.PrivateSvc

	privateBaseURL := cutil.GetHTTPAccess(agentFactoryConf.Host, agentFactoryConf.Port, agentFactoryConf.Protocol)

	impl := &agentFactoryHttpAcc{
		logger:         _logger,
		privateBaseURL: privateBaseURL,
	}

	return impl
}
