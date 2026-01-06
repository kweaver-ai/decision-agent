package httpinject

import (
	"sync"
	"time"

	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-go-common-pkg/src/infra/cmp/cmphelper"
	"github.com/data-agent/agent-app/src/drivenadapter/httpaccess/agentexecutoraccess"
	"github.com/data-agent/agent-app/src/drivenadapter/httpaccess/v2agentexecutoraccess"
	"github.com/data-agent/agent-app/src/infra/cmp/httpclient"
	"github.com/data-agent/agent-app/src/infra/common/global"
	"github.com/data-agent/agent-app/src/port/driven/ihttpaccess/iagentexecutorhttp"
	"github.com/data-agent/agent-app/src/port/driven/ihttpaccess/iv2agentexecutorhttp"
	"github.com/kweaver-ai/kweaver-go-lib/logger"
	"github.com/kweaver-ai/kweaver-go-lib/rest"
)

var (
	agentExecutorOnce   sync.Once
	agentExecutorV1Impl iagentexecutorhttp.IAgentExecutor
	agentExecutorV2Impl iv2agentexecutorhttp.IV2AgentExecutor
)

func initAgentExecutors() {
	agentExecutorOnce.Do(func() {
		agentExecutorConf := global.GConfig.AgentExecutorConf
		log := logger.GetLogger()
		httpClient := cmphelper.GetClient()
		client := rest.NewHTTPClient()
		streamClient := httpclient.NewHTTPClientEx(600 * time.Second)

		agentExecutorV1Impl = agentexecutoraccess.NewAgentExecutorHttpAcc(
			log,
			agentExecutorConf,
			httpClient,
			streamClient,
			client,
		)
		agentExecutorV2Impl = v2agentexecutoraccess.NewV2AgentExecutorHttpAcc(
			log,
			agentExecutorConf,
			client,
			streamClient,
		)
	})
}

// NewAgentExecutorV1HttpAcc 返回 v1 版本的 AgentExecutor 实现
func NewAgentExecutorV1HttpAcc() iagentexecutorhttp.IAgentExecutor {
	initAgentExecutors()
	return agentExecutorV1Impl
}

// NewAgentExecutorV2HttpAcc 返回 v2 版本的 AgentExecutor 实现
func NewAgentExecutorV2HttpAcc() iv2agentexecutorhttp.IV2AgentExecutor {
	initAgentExecutors()
	return agentExecutorV2Impl
}
