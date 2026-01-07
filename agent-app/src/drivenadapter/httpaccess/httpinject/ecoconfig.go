package httpinject

import (
	"sync"

	"github.com/kweaver-ai/decision-agent/agent-app/src/drivenadapter/httpaccess/ecoconfigaccess"
	"github.com/kweaver-ai/decision-agent/agent-app/src/infra/common/global"
	iecoConfighttp "github.com/kweaver-ai/decision-agent/agent-app/src/port/driven/ihttpaccess/iecoconfighttp"
	"github.com/kweaver-ai/kweaver-go-lib/logger"
	"github.com/kweaver-ai/kweaver-go-lib/rest"
)

var (
	ecoConfigOnce sync.Once
	ecoConfigImpl iecoConfighttp.IEcoConfig
)

func NewEcoConfigHttpAcc() iecoConfighttp.IEcoConfig {
	ecoConfigOnce.Do(func() {
		ecoConfigConf := global.GConfig.EcoConfigConf
		ecoConfigImpl = ecoconfigaccess.NewEcoConfigHttpAcc(
			logger.GetLogger(),
			ecoConfigConf,
			rest.NewHTTPClient(),
		)
	})

	return ecoConfigImpl
}
