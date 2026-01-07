package httpinject

import (
	"sync"

	"github.com/kweaver-ai/decision-agent/agent-app/src/drivenadapter/httpaccess/agentfactoryaccess"
	"github.com/kweaver-ai/decision-agent/agent-app/src/infra/common/global"
	"github.com/kweaver-ai/decision-agent/agent-app/src/port/driven/ihttpaccess/iagentfactoryhttp"
	"github.com/kweaver-ai/kweaver-go-lib/logger"
	"github.com/kweaver-ai/kweaver-go-lib/rest"
)

var (
	agentFactoryOnce sync.Once
	agentFactoryImpl iagentfactoryhttp.IAgentFactory
)

func NewAgentFactoryHttpAcc() iagentfactoryhttp.IAgentFactory {
	agentFactoryOnce.Do(func() {
		agentFactoryConf := global.GConfig.AgentFactoryConf
		agentFactoryImpl = agentfactoryaccess.NewAgentFactoryHttpAcc(
			logger.GetLogger(),
			agentFactoryConf,
			rest.NewHTTPClient(),
		)
	})

	return agentFactoryImpl
}
