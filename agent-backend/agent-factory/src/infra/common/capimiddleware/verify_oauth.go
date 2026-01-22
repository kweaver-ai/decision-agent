package capimiddleware

import (
	"context"
	"net/http"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cenum"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cglobal"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/chelper/cenvhelper"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cutil"
	"github.com/kweaver-ai/kweaver-go-lib/rest"

	"github.com/gin-gonic/gin"
)

var hydraInstance rest.Hydra

func GetHydra() rest.Hydra {
	if hydraInstance != nil {
		return hydraInstance
	}

	hydraAdminSetting := rest.HydraAdminSetting{
		HydraAdminHost:     cglobal.GConfig.Hydra.HydraAdmin.Host,
		HydraAdminPort:     cglobal.GConfig.Hydra.HydraAdmin.Port,
		HydraAdminProcotol: "http",
	}
	hydraInstance = rest.NewHydra(hydraAdminSetting)

	return hydraInstance
}

func VerifyOAuthMiddleWare() gin.HandlerFunc {
	hydra := GetHydra()

	return func(c *gin.Context) {
		// 本地调试 mock
		if cenvhelper.IsLocalDev(cenvhelper.RunScenario_Aaron_Local_Dev) {
			visitor := rest.Visitor{
				// ID:      "mock id",
				ID:      "e39adc84-6de8-11f0-b206-4a2c3f0cd493", // 6
				TokenID: "Bearer mock token id",
				Type:    rest.VisitorType_RealName,
				// Type: rest.VisitorType_App,
			}

			ctxKey := cenum.VisitUserInfoCtxKey.String()
			c.Set(ctxKey, &visitor)

			_ctx := context.WithValue(c.Request.Context(), ctxKey, &visitor)
			cutil.UpdateGinReqCtx(c, _ctx)

			c.Next()

			return
		}

		ctx := rest.GetLanguageCtx(c)
		visitor, err := hydra.VerifyToken(ctx, c)

		if err != nil {
			httpError := rest.NewHTTPError(ctx, http.StatusUnauthorized, rest.PublicError_Unauthorized).
				WithErrorDetails(err.Error())
			rest.ReplyError(c, httpError)
			c.Abort()

			return
		}

		ctxKey := cenum.VisitUserInfoCtxKey.String()
		c.Set(ctxKey, &visitor)

		// 设置request context
		_ctx := context.WithValue(c.Request.Context(), ctxKey, &visitor)
		cutil.UpdateGinReqCtx(c, _ctx)

		// 执行后续操作
		c.Next()
	}
}
