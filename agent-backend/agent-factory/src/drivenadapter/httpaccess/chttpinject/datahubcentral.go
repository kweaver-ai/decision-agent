package chttpinject

import (
	"sync"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/httpaccess/datahubcentralhttp"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cglobal"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/ihttpaccess/idatahubacc"
	"github.com/kweaver-ai/kweaver-go-lib/logger"
)

var (
	dataHubCentralOnce sync.Once
	dataHubCentralImpl idatahubacc.IDataHubCentral
)

func NewDataHubCentralHttpAcc() idatahubacc.IDataHubCentral {
	dataHubCentralOnce.Do(func() {
		// 2. dataHubCentral configuration
		dataHubCentralConf := cglobal.GConfig.DataHubCentral

		// 3. dataHubCentral
		dataHubCentralImpl = datahubcentralhttp.NewDataHubHttpAcc(
			logger.GetLogger(),
			dataHubCentralConf,
		)
	})

	return dataHubCentralImpl
}
