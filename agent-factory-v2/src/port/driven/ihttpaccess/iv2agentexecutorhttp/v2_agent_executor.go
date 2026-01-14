package iv2agentexecutorhttp

import (
	"context"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/httpaccess/v2agentexecutoraccess/v2agentexecutordto"
)

// IV2AgentExecutor v2 版本的 Agent Executor 接口
// 注意：ConversationSessionInit 只有 v1 接口，不在此接口中
type IV2AgentExecutor interface {
	Call(ctx context.Context, req *v2agentexecutordto.V2AgentCallReq) (chan string, chan error, error)
}
