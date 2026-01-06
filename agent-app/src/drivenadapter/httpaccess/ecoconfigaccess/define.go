package ecoconfigaccess

import (
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-go-common-pkg/src/infra/cmp/icmp"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-go-common-pkg/src/infra/common/cutil"
	"github.com/data-agent/agent-app/conf"
	iecoConfighttp "github.com/data-agent/agent-app/src/port/driven/ihttpaccess/iecoconfighttp"
	"github.com/kweaver-ai/kweaver-go-lib/rest"
)

type ecoConfigHttpAcc struct {
	logger         icmp.Logger
	client         rest.HTTPClient
	ecoConfigConf  *conf.EcoConfigConf
	privateAddress string
}

var _ iecoConfighttp.IEcoConfig = &ecoConfigHttpAcc{}

func NewEcoConfigHttpAcc(logger icmp.Logger, ecoConfigConf *conf.EcoConfigConf, client rest.HTTPClient) iecoConfighttp.IEcoConfig {
	impl := &ecoConfigHttpAcc{
		logger:         logger,
		client:         client,
		ecoConfigConf:  ecoConfigConf,
		privateAddress: cutil.GetHTTPAccess(ecoConfigConf.PrivateSvc.Host, ecoConfigConf.PrivateSvc.Port, ecoConfigConf.PrivateSvc.Protocol),
	}

	return impl
}
