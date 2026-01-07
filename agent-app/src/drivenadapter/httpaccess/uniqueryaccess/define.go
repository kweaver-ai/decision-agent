package uniqueryaccess

import (
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/conf"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/port/driven/ihttpaccess/iuniqueryhttp"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-go-common-pkg/src/infra/cmp/icmp"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-go-common-pkg/src/infra/common/cutil"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/mdl-go-lib/rest"
)

type uniqueryHttpAcc struct {
	logger         icmp.Logger
	client         rest.HTTPClient
	uniqueryConf   *conf.UniqueryConf
	privateAddress string
}

var _ iuniqueryhttp.IUniquery = &uniqueryHttpAcc{}

func NewUniqueryHttpAcc(logger icmp.Logger, uniqueryConf *conf.UniqueryConf, client rest.HTTPClient) iuniqueryhttp.IUniquery {
	impl := &uniqueryHttpAcc{
		logger:         logger,
		client:         client,
		uniqueryConf:   uniqueryConf,
		privateAddress: cutil.GetHTTPAccess(uniqueryConf.PrivateSvc.Host, uniqueryConf.PrivateSvc.Port, uniqueryConf.PrivateSvc.Protocol),
	}

	return impl
}
