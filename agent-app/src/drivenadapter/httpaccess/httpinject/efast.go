package httpinject

import (
	"sync"

	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-go-common-pkg/src/infra/cmp/cmphelper"
	"github.com/data-agent/agent-app/src/drivenadapter/httpaccess/efastaccess"
	"github.com/data-agent/agent-app/src/infra/common/global"
	"github.com/data-agent/agent-app/src/port/driven/ihttpaccess/iefasthttp"
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
