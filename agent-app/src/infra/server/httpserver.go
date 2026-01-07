package server

import (
	"context"
	"fmt"
	"net/http"

	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/driveradapter/api/httphandler"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/driveradapter/api/httphandler/agenthandler"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/driveradapter/api/httphandler/conversationhandler"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/driveradapter/api/httphandler/observabilityhandler"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/driveradapter/api/httphandler/sessionhandler"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/driveradapter/api/httphandler/tempareahandler"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/infra/common/global"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/port/driver/ihandlerportdriver"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-go-common-pkg/src/infra/common/capimiddleware"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-go-common-pkg/src/infra/common/chelper/cenvhelper"
	"github.com/gin-gonic/gin"
)

type httpServer struct {
	// HTTP 服务器实例
	httpSrv *http.Server
	// 健康检查
	httpHealthHandler ihandlerportdriver.IHTTPRouter

	// agent 对话
	agentHandler ihandlerportdriver.IHTTPRouter

	// conversation
	conversationHandler ihandlerportdriver.IHTTPRouter

	// temparea
	tempareaHandler ihandlerportdriver.IHTTPRouter

	// observability
	observabilityHandler ihandlerportdriver.IHTTPRouter

	// session
	sessionHandler ihandlerportdriver.IHTTPRouter
}

func NewHTTPServer() IServer {
	s := &httpServer{
		httpHealthHandler:    httphandler.NewHTTPHealthHandler(),
		agentHandler:         agenthandler.NewAgentHTTPHandler(),
		conversationHandler:  conversationhandler.NewConversationHTTPHandler(),
		tempareaHandler:      tempareahandler.NewTempareaHTTPHandler(),
		observabilityHandler: observabilityhandler.NewObservabilityHTTPHandler(),
		sessionHandler:       sessionhandler.NewSessionHTTPHandler(),
	}

	return s
}

func (s *httpServer) Start() {
	go func() {
		// 设置为 release 模式（屏蔽 debug 日志）
		gin.SetMode(gin.ReleaseMode)
		engine := gin.New()
		// engine.Use(gin.Logger())

		// 注册路由 - 健康检查
		routerHealth := engine.Group("/health")
		s.httpHealthHandler.RegPriRouter(routerHealth)

		// 注册路由 - public & private
		s.pubRouter(engine)
		s.priRouter(engine)

		url := fmt.Sprintf("%s:%d", global.GConfig.Project.Host, global.GConfig.Project.Port)
		fmt.Printf("http server start at %s\n", url)
		// 创建 HTTP 服务器
		s.httpSrv = &http.Server{
			Addr:    url,
			Handler: engine,
		}

		// 启动服务器
		err := s.httpSrv.ListenAndServe()
		if err != nil && err != http.ErrServerClosed {
			err = fmt.Errorf("http server start failed, err: %w", err)
			panic(err)
		}
	}()
}

// Shutdown 优雅关闭服务器
func (s *httpServer) Shutdown(ctx context.Context) error {
	if s.httpSrv == nil {
		return nil
	}

	// 直接使用传入的上下文，由调用方控制超时
	return s.httpSrv.Shutdown(ctx)
}

func (s *httpServer) pubRouter(engine *gin.Engine) {
	router := engine.Group("/api/agent-app/v1")

	if cenvhelper.IsLocalDev(cenvhelper.RunScenario_Aaron_Local_Dev) {
		router.Use(capimiddleware.Cors())

		// 添加通用OPTIONS路由处理CORS预检请求
		router.OPTIONS("/*path", func(c *gin.Context) {})
	}

	router.Use(
		capimiddleware.Recovery(),
		capimiddleware.RequestLoggerV2Middleware(),
		// 获取访问语言
		capimiddleware.Language(),
		// 新增 Hydra 接口鉴权，开发环境可以临时屏蔽
		capimiddleware.VerifyOAuthMiddleWare(),
		// 可观测 Trace 中间件
		capimiddleware.O11yTraceMiddleware(),
		// 注入业务域id
		capimiddleware.HandleBizDomain(true),
	)
	s.agentHandler.RegPubRouter(router)
	s.conversationHandler.RegPubRouter(router)
	s.tempareaHandler.RegPubRouter(router)
	s.observabilityHandler.RegPubRouter(router)
	s.sessionHandler.RegPubRouter(router)
}

func (s *httpServer) priRouter(engine *gin.Engine) {
	internalRouterG := engine.Group("/api/agent-app/internal/v1")

	internalRouterG.Use(
		capimiddleware.Recovery(),
		capimiddleware.RequestLoggerV2Middleware(),
		// 注入业务域id
		capimiddleware.HandleBizDomain(true),
	)
	s.agentHandler.RegPriRouter(internalRouterG)
	s.conversationHandler.RegPriRouter(internalRouterG)
	s.observabilityHandler.RegPriRouter(internalRouterG)
}
