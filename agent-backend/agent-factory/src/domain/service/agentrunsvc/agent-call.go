package agentsvc

import (
	"context"
	"fmt"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/httpaccess/agentexecutoraccess/agentexecutordto"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/httpaccess/v2agentexecutoraccess"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/ihttpaccess/iagentexecutorhttp"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/ihttpaccess/iv2agentexecutorhttp"
)

type AgentCall struct {
	callCtx         context.Context
	req             *agentexecutordto.AgentCallReq
	agentExecutorV1 iagentexecutorhttp.IAgentExecutor
	agentExecutorV2 iv2agentexecutorhttp.IV2AgentExecutor
	cancelFunc      context.CancelFunc
}

func (a *AgentCall) Call() (chan string, chan error, error) {
	if a.req.ExecutorVersion == "v2" && a.agentExecutorV2 != nil {
		v2Req := v2agentexecutoraccess.ConvertV1ToV2CallReq(a.req)
		return a.agentExecutorV2.Call(a.callCtx, v2Req)
	}

	if a.req.ExecutorVersion == "v1" && a.agentExecutorV1 != nil {
		return a.agentExecutorV1.Call(a.callCtx, a.req)
	}

	return nil, nil, fmt.Errorf("executor version %s not supported", a.req.ExecutorVersion)
}

func (a *AgentCall) Resume() {

}

func (a *AgentCall) Cancel() {
	a.cancelFunc()
}
