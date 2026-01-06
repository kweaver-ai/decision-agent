package sessionsvc

import (
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-go-common-pkg/src/infra/cmp/icmp"
	"github.com/data-agent/agent-app/src/port/driven/ihttpaccess/iagentexecutorhttp"
	"github.com/data-agent/agent-app/src/port/driven/iredisaccess/isessionredis"
	"github.com/data-agent/agent-app/src/port/driver/iportdriver"
)

type sessionSvc struct {
	logger          icmp.Logger
	sessionRedisAcc isessionredis.ISessionRedisAcc
	agentExecutorV1 iagentexecutorhttp.IAgentExecutor
}

var _ iportdriver.ISessionSvc = &sessionSvc{}

type NewSessionSvcDto struct {
	Logger          icmp.Logger
	SessionRedis    isessionredis.ISessionRedisAcc
	AgentExecutorV1 iagentexecutorhttp.IAgentExecutor
}

func NewSessionService(dto *NewSessionSvcDto) iportdriver.ISessionSvc {
	return &sessionSvc{
		logger:          dto.Logger,
		sessionRedisAcc: dto.SessionRedis,
		agentExecutorV1: dto.AgentExecutorV1,
	}
}
