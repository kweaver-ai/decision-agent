package agentfactoryaccess

import (
	"github.com/kweaver-ai/decision-agent/agent-app/conf"
	"github.com/kweaver-ai/decision-agent/agent-app/src/port/driven/ihttpaccess/iagentfactoryhttp"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/cmp/icmp"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/cutil"
	"github.com/kweaver-ai/kweaver-go-lib/rest"
)

type agentFactoryHttpAcc struct {
	logger           icmp.Logger
	client           rest.HTTPClient
	agentFactoryConf *conf.AgentFactoryConf
	privateAddress   string
}

var _ iagentfactoryhttp.IAgentFactory = &agentFactoryHttpAcc{}

func NewAgentFactoryHttpAcc(logger icmp.Logger, agentFactoryConf *conf.AgentFactoryConf, client rest.HTTPClient) iagentfactoryhttp.IAgentFactory {
	impl := &agentFactoryHttpAcc{
		logger:           logger,
		client:           client,
		agentFactoryConf: agentFactoryConf,
		privateAddress:   cutil.GetHTTPAccess(agentFactoryConf.PrivateSvc.Host, agentFactoryConf.PrivateSvc.Port, agentFactoryConf.PrivateSvc.Protocol),
	}

	return impl
}
