package dainject

import (
	"sync"

	"github.com/kweaver-ai/decision-agent/agent-app/src/domain/service/observabilitysvc"
	"github.com/kweaver-ai/decision-agent/agent-app/src/drivenadapter/httpaccess/httpinject"
	"github.com/kweaver-ai/decision-agent/agent-app/src/port/driver/iportdriver"
	"github.com/kweaver-ai/kweaver-go-lib/logger"
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
