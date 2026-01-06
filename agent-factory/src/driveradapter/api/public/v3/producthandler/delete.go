package producthandler

import (
	"net/http"

	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-factory/src/domain/constant/auditconstant"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/capierr"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/capimiddleware"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/chelper"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/cutil"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/mdl-go-lib/audit"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/mdl-go-lib/rest"
	"github.com/gin-gonic/gin"
)

func (h *productHTTPHandler) Delete(c *gin.Context) {
	isPrivate := capimiddleware.IsInternalAPI(c)

	var visitor *rest.Visitor

	if !isPrivate {
		visitor = chelper.GetVisitorFromCtx(c.Request.Context())
	}

	id := c.Param("id")
	if id == "" {
		err := capierr.New400Err(c, "id is empty")
		if !isPrivate {
			audit.NewWarnLogWithError(audit.OPERATION, auditconstant.DELETE, audit.TransforOperator(*visitor),
				auditconstant.GenerateProductAuditObject("", ""), &err.BaseError)
		}

		_ = c.Error(err)

		return
	}

	auditloginfo, err := h.productService.Delete(c, cutil.MustParseInt64(id))
	if err != nil {
		httpErr := capierr.New500Err(c, err.Error())
		if !isPrivate {
			audit.NewWarnLogWithError(audit.OPERATION, auditconstant.DELETE, audit.TransforOperator(*visitor),
				auditconstant.GenerateProductAuditObject(auditloginfo.ID, auditloginfo.Name), &httpErr.BaseError)
		}

		_ = c.Error(err)

		return
	}

	if !isPrivate {
		audit.NewWarnLog(audit.OPERATION, auditconstant.DELETE, audit.TransforOperator(*visitor),
			auditconstant.GenerateProductAuditObject(auditloginfo.ID, auditloginfo.Name), audit.SUCCESS, "")
	}

	c.Status(http.StatusNoContent)
}
