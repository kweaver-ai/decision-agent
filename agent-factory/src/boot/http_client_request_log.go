package boot

import (
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/chelper/cenvhelper"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/chelper/httphelper"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/chelper/httprequesthelper"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/mdl-go-lib/logger"
)

// initHTTPClientRequestLog 初始化HTTP客户端请求日志记录器
// 注意：这个是当本服务的HTTP客户端发起请求其他服务的接口等时，记录的请求日志。不是记录接受到的请求的日志
func initHTTPClientRequestLog() {
	// 日志目录
	logDir := "log/dependence_http_requests"
	if cenvhelper.IsLocalDev() {
		logDir = "/Users/Zhuanz/Work/as/dip_ws/agent-factory/.local/log/dependence_http_requests"
	}

	// 配置请求日志记录器
	isDebugMode := cenvhelper.IsDebugMode()
	config := &httprequesthelper.Config{
		Enabled:             isDebugMode,
		OutputMode:          httprequesthelper.OutputModeFile, // 输出到文件
		LogDir:              logDir,
		FileNamePattern:     "requests_2006-01-02.log",
		PrettyJSON:          false, // 生产环境不格式化JSON
		MaxBodySize:         10 * 1024,
		IncludeHeaders:      true,
		IncludeResponseBody: true,
	}

	// 本地开发环境同时输出到控制台
	if cenvhelper.IsLocalDev() {
		// config.OutputMode = httprequesthelper.OutputModeBoth
		// config.PrettyJSON = true
	}

	// 启用请求日志记录
	if err := httphelper.EnableHTTPClientRequestLogging(config); err != nil {
		logger.GetLogger().Errorf("Failed to enable request logging: %v", err)
	}
}
