package datahubcentralhttp

import (
	"github.com/kweaver-ai/decision-agent/agent-factory/cconf"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/cmp/icmp"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cutil"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/ihttpaccess/idatahubacc"
)

type dataHubHttpAcc struct {
	logger         icmp.Logger
	dataHubConf    *cconf.DataHubCentralConf
	privateAddress string
}

var _ idatahubacc.IDataHubCentral = &dataHubHttpAcc{}

func NewDataHubHttpAcc(
	_logger icmp.Logger, dataHubConf *cconf.DataHubCentralConf,
) idatahubacc.IDataHubCentral {
	impl := &dataHubHttpAcc{
		logger:         _logger,
		dataHubConf:    dataHubConf,
		privateAddress: cutil.GetHTTPAccess(dataHubConf.PrivateSvc.Host, dataHubConf.PrivateSvc.Port, dataHubConf.PrivateSvc.Protocol),
	}

	return impl
}
