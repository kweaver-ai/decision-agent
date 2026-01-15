package chttpinject

import (
	"sync"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/httpaccess/agentfactoryhttp"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/ihttpaccess/iagentfactoryacc"
	"github.com/kweaver-ai/kweaver-go-lib/logger"
)

var (
	authFactoryOnce sync.Once
	authFactoryImpl iagentfactoryacc.IAgentFactoryHttpAcc
)

func NewAgentFactoryHttpAcc() iagentfactoryacc.IAgentFactoryHttpAcc {
	authFactoryOnce.Do(func() {
		authFactoryImpl = agentfactoryhttp.NewAgentFactoryHttpAcc(
			logger.GetLogger(),
		)
	})

	return authFactoryImpl
}
