package efastaccess

import (
	"github.com/kweaver-ai/decision-agent/agent-factory/conf"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/ihttpaccess/iefasthttp"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/cmp/icmp"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cutil"
	"github.com/kweaver-ai/kweaver-go-lib/rest"
)

type efastHttpAcc struct {
	logger         icmp.Logger
	httpClient     icmp.IHttpClient
	client         rest.HTTPClient
	efastConf      *conf.EfastConf
	privateAddress string
}

var _ iefasthttp.IEfast = &efastHttpAcc{}

func NewEfastHttpAcc(logger icmp.Logger, efastConf *conf.EfastConf, httpClient icmp.IHttpClient, client rest.HTTPClient) iefasthttp.IEfast {
	impl := &efastHttpAcc{
		logger:         logger,
		httpClient:     httpClient,
		client:         client,
		efastConf:      efastConf,
		privateAddress: cutil.GetHTTPAccess(efastConf.PrivateSvc.Host, efastConf.PrivateSvc.Port, efastConf.PrivateSvc.Protocol),
	}

	return impl
}
