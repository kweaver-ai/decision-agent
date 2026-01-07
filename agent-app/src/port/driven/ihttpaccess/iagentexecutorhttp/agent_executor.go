package iagentexecutorhttp

import (
	"context"

	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/drivenadapter/httpaccess/agentexecutoraccess/agentexecutoraccreq"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/drivenadapter/httpaccess/agentexecutoraccess/agentexecutoraccres"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/drivenadapter/httpaccess/agentexecutoraccess/agentexecutordto"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-go-common-pkg/src/infra/common/ctype"
)

type IAgentExecutor interface {
	Call(ctx context.Context, req *agentexecutordto.AgentCallReq) (chan string, chan error, error)
	// ConversationSessionInit(ctx context.Context, req *agentexecutoraccreq.ConversationSessionInitReq, visitorInfo *ctype.VisitorInfo) (resp agentexecutoraccres.ConversationSessionInitResp, err error)
	AgentCacheManage(ctx context.Context, req *agentexecutoraccreq.AgentCacheManageReq, visitorInfo *ctype.VisitorInfo) (resp agentexecutoraccres.AgentCacheManageResp, err error)
}
