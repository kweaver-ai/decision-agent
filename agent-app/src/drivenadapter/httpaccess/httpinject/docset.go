package httpinject

import (
	"sync"

	"github.com/kweaver-ai/decision-agent/agent-app/src/drivenadapter/httpaccess/docsetaccess"
	"github.com/kweaver-ai/decision-agent/agent-app/src/infra/common/global"
	"github.com/kweaver-ai/decision-agent/agent-app/src/port/driven/ihttpaccess/idocsethttp"
	"github.com/kweaver-ai/kweaver-go-lib/logger"
	"github.com/kweaver-ai/kweaver-go-lib/rest"
)

var (
	docsetOnce sync.Once
	docsetImpl idocsethttp.IDocset
)

func NewDocsetHttpAcc() idocsethttp.IDocset {
	docsetOnce.Do(func() {
		docsetConf := global.GConfig.DocsetConf
		docsetImpl = docsetaccess.NewDocsetHttpAcc(
			logger.GetLogger(),
			docsetConf,
			rest.NewHTTPClient(),
		)
	})

	return docsetImpl
}
