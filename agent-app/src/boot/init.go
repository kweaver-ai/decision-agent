package boot

import (
	"github.com/kweaver-ai/decision-agent/agent-app/conf"
	_ "github.com/kweaver-ai/decision-agent/agent-app/src/infra/apierr"
	"github.com/kweaver-ai/decision-agent/agent-app/src/infra/common"
	"github.com/kweaver-ai/decision-agent/agent-app/src/infra/common/global"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/cglobal"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/chelper/redishelper"
	"github.com/kweaver-ai/kweaver-go-lib/logger"
)

// 初始化
func Init() {
	global.GConfig = conf.NewConfig()
	cglobal.GConfig = global.GConfig.Config

	global.GDB = common.NewDBPool() // 初始化全局DB
	cglobal.GDB = global.GDB

	// 初始化Redis
	redishelper.ConnectRedis(&global.GConfig.Redis)

	logFile := "/app/agent-app/logs/agent-app.log"
	// new 2025年04月16日14:42:00
	// logger 初始化
	lggerSetting := logger.LogSetting{
		LogServiceName: "agent-app",
		LogLevel:       global.GConfig.GetLogLevelString(),
		LogFileName:    logFile,
		MaxAge:         30,
		MaxBackups:     10,
		MaxSize:        100,
	}
	logger.InitGlobalLogger(lggerSetting)

	// 设置http server request log (记录接收到的请求)
	initHTTPServerRequestLog()
}
