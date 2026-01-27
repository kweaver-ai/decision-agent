package dainject

import (
	"sync"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/service"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/service/tempareasvc"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/dbaccess/tempareadbacc"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/httpaccess/httpinject"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driver/iportdriver"
	"github.com/kweaver-ai/kweaver-go-lib/logger"
)

var (
	tempAreaSvcOnce sync.Once
	tempAreaSvcImpl iportdriver.ITempAreaSvc
)

func NewTempAreaSvc() iportdriver.ITempAreaSvc {
	tempAreaSvcOnce.Do(func() {
		dto := &tempareasvc.NewTempAreaSvcDto{
			SvcBase:      service.NewSvcBase(),
			Logger:       logger.GetLogger(),
			TempAreaRepo: tempareadbacc.NewTempAreaRepo(),
			AgentFactory: httpinject.NewAgentFactoryHttpAcc(),
			EcoConfig:    httpinject.NewEcoConfigHttpAcc(),
		}
		tempAreaSvcImpl = tempareasvc.NewTempAreaService(dto)
	})

	return tempAreaSvcImpl
}
