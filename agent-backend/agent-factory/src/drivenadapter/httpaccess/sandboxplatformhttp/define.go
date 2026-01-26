package sandboxplatformhttp

import (
	"sync"

	"github.com/kweaver-ai/decision-agent/agent-factory/cconf"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/cmp/httpclient"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/cmp/icmp"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cutil"
)

type sandboxPlatformHttpAcc struct {
	logger           icmp.Logger
	httpClient       httpclient.HTTPClient
	sandboxPlatformConf *conf.SandboxPlatformConf
	baseURL          string
}

var (
	sandboxPlatformOnce sync.Once
	sandboxPlatformImpl ISandboxPlatform
)

func NewSandboxPlatformHttpAcc(sandboxPlatformConf *conf.SandboxPlatformConf, httpClient httpclient.HTTPClient, logger icmp.Logger) ISandboxPlatform {
	sandboxPlatformOnce.Do(func() {
		sandboxPlatformImpl = &sandboxPlatformHttpAcc{
			logger:             logger,
			httpClient:       httpClient,
			sandboxPlatformConf: sandboxPlatformConf,
			baseURL:          cutil.GetHTTPAccess(sandboxPlatformConf.Svc.Host, sandboxPlatformConf.Svc.Port, sandboxPlatformConf.Svc.Protocol),
		}
	})
	return sandboxPlatformImpl
}
