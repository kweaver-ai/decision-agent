package ecoindexhttp

import (
	"github.com/kweaver-ai/decision-agent/agent-factory/cconf"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/cmp/icmp"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cutil"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/ihttpaccess/iecoindex"
)

type ecoIndexHttpAcc struct {
	logger         icmp.Logger
	httpClient     icmp.IHttpClient
	ecoConf        *cconf.EcoIndexConf
	privateAddress string
}

var _ iecoindex.IEcoIndex = &ecoIndexHttpAcc{}

func NewEcoIndexHttpAcc(
	_logger icmp.Logger, ecoConf *cconf.EcoIndexConf,
	httpClient icmp.IHttpClient,
) iecoindex.IEcoIndex {
	impl := &ecoIndexHttpAcc{
		logger:         _logger,
		httpClient:     httpClient,
		ecoConf:        ecoConf,
		privateAddress: cutil.GetHTTPAccess(ecoConf.PrivateSvc.Host, ecoConf.PrivateSvc.Port, ecoConf.PrivateSvc.Protocol),
	}

	return impl
}
