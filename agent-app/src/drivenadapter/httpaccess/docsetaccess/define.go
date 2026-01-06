package docsetaccess

import (
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-go-common-pkg/src/infra/cmp/icmp"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-go-common-pkg/src/infra/common/cutil"
	"github.com/data-agent/agent-app/conf"
	"github.com/data-agent/agent-app/src/port/driven/ihttpaccess/idocsethttp"
	"github.com/kweaver-ai/kweaver-go-lib/rest"
)

type docsetHttpAcc struct {
	logger         icmp.Logger
	client         rest.HTTPClient
	docsetConf     *conf.DocsetConf
	privateAddress string
}

var _ idocsethttp.IDocset = &docsetHttpAcc{}

func NewDocsetHttpAcc(logger icmp.Logger, docsetConf *conf.DocsetConf, httpClient rest.HTTPClient) idocsethttp.IDocset {
	impl := &docsetHttpAcc{
		logger:         logger,
		client:         httpClient,
		docsetConf:     docsetConf,
		privateAddress: cutil.GetHTTPAccess(docsetConf.PrivateSvc.Host, docsetConf.PrivateSvc.Port, docsetConf.PrivateSvc.Protocol),
	}

	return impl
}
