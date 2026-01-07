package dainject

import (
	"sync"

	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/domain/service/observabilitysvc"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/drivenadapter/httpaccess/httpinject"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/port/driver/iportdriver"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/mdl-go-lib/logger"
)

var (
	observabilitySvcOnce sync.Once
	observabilitySvcImpl iportdriver.IObservability
)

func NewObservabilitySvc() iportdriver.IObservability {
	observabilitySvcOnce.Do(func() {
		dto := &observabilitysvc.NewObservabilitySvcDto{
			Logger:       logger.GetLogger(),
			Uniquery:     httpinject.NewUniqueryHttpAcc(),
			AgentFactory: httpinject.NewAgentFactoryHttpAcc(),
		}

		observabilitySvcImpl = observabilitysvc.NewObservabilitySvc(dto)
	})

	return observabilitySvcImpl
}
