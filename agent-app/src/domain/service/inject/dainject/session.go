package dainject

import (
	"sync"

	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/domain/service/sessionsvc"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/drivenadapter/httpaccess/httpinject"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/drivenadapter/redisaccess/sessionredisacc"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/port/driver/iportdriver"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/mdl-go-lib/logger"
)

var (
	sessionSvcOnce sync.Once
	sessionSvcImpl iportdriver.ISessionSvc
)

func NewSessionSvc() iportdriver.ISessionSvc {
	sessionSvcOnce.Do(func() {
		dto := &sessionsvc.NewSessionSvcDto{
			Logger:          logger.GetLogger(),
			SessionRedis:    sessionredisacc.NewSessionRedisAcc(),
			AgentExecutorV1: httpinject.NewAgentExecutorV1HttpAcc(),
		}
		sessionSvcImpl = sessionsvc.NewSessionService(dto)
	})

	return sessionSvcImpl
}
