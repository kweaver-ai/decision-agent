package dainject

import (
	"sync"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/service"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/service/dssvc"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/dbaccess/datasetdbacc"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/dbaccess/dsdbacc"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/httpaccess/httpinject"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driver/iv3portdriver"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/cmp/rediscmp"
	"github.com/kweaver-ai/kweaver-go-lib/logger"
)

var (
	dsSvcOnce sync.Once
	dsSvcImpl iv3portdriver.IDsSvc
)

func NewDsSvc() iv3portdriver.IDsSvc {
	dsSvcOnce.Do(func() {
		dto := &dssvc.NewDsSvcDto{
			RedisCmp:           rediscmp.NewRedisCmp(),
			SvcBase:            service.NewSvcBase(),
			DsRepo:             dsdbacc.NewDsRepo(),
			EcoIndexHttp:       httpinject.NewEcoIndexHttpAcc(),
			DatasetRepo:        datasetdbacc.NewDatasetRepo(),
			DatahubCentralHttp: httpinject.NewDataHubCentralHttpAcc(),
			Logger:             logger.GetLogger(),
		}

		dsSvcImpl = dssvc.NewDsSvc(dto)
	})

	return dsSvcImpl
}
