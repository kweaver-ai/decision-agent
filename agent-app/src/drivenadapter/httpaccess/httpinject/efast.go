package httpinject

import (
	"sync"

	"github.com/kweaver-ai/decision-agent/agent-app/src/drivenadapter/httpaccess/efastaccess"
	"github.com/kweaver-ai/decision-agent/agent-app/src/infra/common/global"
	"github.com/kweaver-ai/decision-agent/agent-app/src/port/driven/ihttpaccess/iefasthttp"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/cmp/cmphelper"
	"github.com/kweaver-ai/kweaver-go-lib/logger"
	"github.com/kweaver-ai/kweaver-go-lib/rest"
)

var (
	efastOnce sync.Once
	efastImpl iefasthttp.IEfast
)

func NewEfastHttpAcc() iefasthttp.IEfast {
	efastOnce.Do(func() {
		efastConf := global.GConfig.EfastConf
		efastImpl = efastaccess.NewEfastHttpAcc(
			logger.GetLogger(),
			efastConf,
			cmphelper.GetClient(),
			rest.NewHTTPClient(),
		)
	})

	return efastImpl
}
