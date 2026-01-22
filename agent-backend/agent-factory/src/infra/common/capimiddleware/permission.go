package capimiddleware

import (
	"github.com/gin-gonic/gin"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/httpaccess/agentfactoryhttp/afhttpdto"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/httpaccess/chttpinject"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/capierr"
	"github.com/kweaver-ai/kweaver-go-lib/rest"
	"github.com/pkg/errors"
)

// CheckPms 使用示例：见`CheckAgentUsePmsDemo`
func CheckPms(req *afhttpdto.CheckPmsReq, clb func(c *gin.Context, hasPms bool)) gin.HandlerFunc {
	return func(c *gin.Context) {
		if err := req.ReqCheck(); err != nil {
			err = errors.Wrap(err, "capimiddleware: [CheckPms]: req check error")
			httpErr := capierr.New400Err(c, err.Error())
			rest.ReplyError(c, httpErr)
			c.Abort()

			return
		}

		if !req.IsAgentUseCheck() {
			panic("capimiddleware: [CheckPms]: 目前只支持检查Agent使用权限")
		}

		if clb == nil {
			panic("capimiddleware: [CheckPms]: clb is nil")
		}

		hasPms, err := chttpinject.NewAgentFactoryHttpAcc().CheckAgentUsePermission(c, req)
		if err != nil {
			err = errors.Wrap(err, "middleware: [CheckPms]: http CheckAgentUsePermission error")
			rest.ReplyError(c, err)
			c.Abort()

			return
		}

		clb(c, hasPms)
	}
}
