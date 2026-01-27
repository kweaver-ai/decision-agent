package httpinject

import (
	"sync"

	"github.com/kweaver-ai/decision-agent/agent-factory/port/driven/ihttpaccess/isandboxplatformhttp"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/httpaccess/sandboxplatformhttp"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/global"
	"github.com/kweaver-ai/kweaver-go-lib/logger"
	"github.com/kweaver-ai/kweaver-go-lib/rest"
)

var (
	sandboxPlatformOnce sync.Once
	sandboxPlatformImpl isandboxplatformhttp.ISandboxPlatform
)

func NewSandboxPlatformHttpAcc() isandboxplatformhttp.ISandboxPlatform {
	sandboxPlatformOnce.Do(func() {
		sandboxPlatformConf := global.GConfig.SandboxPlatformConf

		if global.GConfig.MockSandboxPlatform {
			sandboxPlatformImpl = sandboxplatformhttp.NewMockSandboxPlatform(logger.GetLogger())
		} else {
			sandboxPlatformImpl = sandboxplatformhttp.NewSandboxPlatformHttpAcc(
				sandboxPlatformConf,
				rest.NewHTTPClient(),
				logger.GetLogger(),
			)
		}
	})

	return sandboxPlatformImpl
}
