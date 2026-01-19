package httpserver

import (
	"github.com/gin-gonic/gin"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/apimiddleware"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/capimiddleware"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/chelper/cenvhelper"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/global"
	"go.opentelemetry.io/contrib/instrumentation/github.com/gin-gonic/gin/otelgin"
)

// registerManagementPubRoutes 注册Management侧公开路由 (V3)
func (s *httpServer) registerManagementPubRoutes(engine *gin.Engine) {
	router := engine.Group("/api/agent-factory/v3")

	// 外部接口默认不使用默认业务域
	isUseDefaultBizDomain := false

	if cenvhelper.IsLocalDev() {
		isUseDefaultBizDomain = true

		router.Use(capimiddleware.Cors())

		// 添加通用OPTIONS路由处理CORS预检请求
		router.OPTIONS("/*path", func(c *gin.Context) {})
	}

	router.Use(
		capimiddleware.Recovery(),
		capimiddleware.RequestLoggerV2Middleware(),
		capimiddleware.ErrorHandler(),
		// 获取访问语言
		capimiddleware.Language(),
		// 新增 Hydra 接口鉴权，开发环境可以临时屏蔽
		capimiddleware.VerifyOAuthMiddleWare(),
		// 业务域
		capimiddleware.HandleBizDomain(isUseDefaultBizDomain),
		apimiddleware.VisitorTypeCheck(),

		// 注入OpenTelemetry中间件
		otelgin.Middleware(global.GConfig.OtelConfig.ServiceName),
		// 注入logs和metrics
		global.GDependencyInjector.Middleware(),
	)

	s.v3AgentConfigHandler.RegPubRouter(router)
	s.v3AgentTplHandler.RegPubRouter(router)
	s.productHandler.RegPubRouter(router)
	s.categoryHandler.RegPubRouter(router)
	s.releaseHandler.RegPubRouter(router)
	s.squareHandler.RegPubRouter(router)
	s.permissionHandler.RegPubRouter(router)
	s.publishedHandler.RegPubRouter(router)

	s.personalSpaceHandler.RegPubRouter(router)
	s.otherHandler.RegPubRouter(router)
	s.testHandler.RegPubRouter(router)
	s.anysharedsHandler.RegPubRouter(router)
}

// registerManagementPriRoutes 注册Management侧私有路由 (V3)
func (s *httpServer) registerManagementPriRoutes(engine *gin.Engine) {
	internalRouterG := engine.Group("/api/agent-factory/internal/v3")

	// 内部接口默认使用默认业务域
	isUseDefaultBizDomain := true

	internalRouterG.Use(
		capimiddleware.Recovery(),
		capimiddleware.ErrorHandler(),
		capimiddleware.RequestLoggerV2Middleware(),
		capimiddleware.Language(),
		capimiddleware.HandleBizDomain(isUseDefaultBizDomain),

		// 注入OpenTelemetry中间件
		otelgin.Middleware(global.GConfig.OtelConfig.ServiceName),
		// 注入logs和metrics
		global.GDependencyInjector.Middleware(),
	)

	s.releaseHandler.RegPriRouter(internalRouterG)
	s.v3AgentConfigHandler.RegPriRouter(internalRouterG)
	s.v3AgentTplHandler.RegPriRouter(internalRouterG)
	s.squareHandler.RegPriRouter(internalRouterG)
	s.publishedHandler.RegPriRouter(internalRouterG)
	s.permissionHandler.RegPriRouter(internalRouterG)
	s.otherHandler.RegPriRouter(internalRouterG)
	s.testHandler.RegPriRouter(internalRouterG)
}
