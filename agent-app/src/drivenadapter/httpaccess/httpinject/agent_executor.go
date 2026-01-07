package httpinject

import (
	"sync"
	"time"

	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/drivenadapter/httpaccess/agentexecutoraccess"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/drivenadapter/httpaccess/v2agentexecutoraccess"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/infra/cmp/httpclient"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/infra/common/global"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/port/driven/ihttpaccess/iagentexecutorhttp"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/port/driven/ihttpaccess/iv2agentexecutorhttp"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-go-common-pkg/src/infra/cmp/cmphelper"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/mdl-go-lib/logger"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/mdl-go-lib/rest"
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
