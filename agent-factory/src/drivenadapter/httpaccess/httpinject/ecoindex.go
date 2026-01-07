package httpinject

import (
	"sync"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/global"
	"github.com/kweaver-ai/agent-go-common-pkg/src/drivenadapter/httpaccess/ecoindexhttp"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/chelper/httphelper"
	"github.com/kweaver-ai/agent-go-common-pkg/src/port/driven/ihttpaccess/iecoindex"
	"github.com/kweaver-ai/kweaver-go-lib/logger"
)

var (
	ecoIndexOnce sync.Once
	ecoIndexImpl iecoindex.IEcoIndex
)

func NewEcoIndexHttpAcc() iecoindex.IEcoIndex {
	ecoIndexOnce.Do(func() {
		// 2. ecoIndex configuration
		ecoConf := global.GConfig.EcoIndex

		// 3. ecoIndex
		ecoIndexImpl = ecoindexhttp.NewEcoIndexHttpAcc(
			logger.GetLogger(),
			ecoConf,
			httphelper.NewHTTPClient(),
		)
	})

	return ecoIndexImpl
}
