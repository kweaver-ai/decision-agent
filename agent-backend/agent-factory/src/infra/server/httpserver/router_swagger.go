package httpserver

import (
	"github.com/gin-gonic/gin"
	_ "github.com/kweaver-ai/decision-agent/agent-factory/docs"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/global"
	swaggerFiles "github.com/swaggo/files"
	ginSwagger "github.com/swaggo/gin-swagger"
)

// registerSwaggerRoutes 注册 Swagger UI 路由
func (s *httpServer) registerSwaggerRoutes(engine *gin.Engine) {
	if !global.GConfig.EnableSwagger {
		return
	}

	engine.GET("/swagger/*any", ginSwagger.WrapHandler(swaggerFiles.Handler))
}
