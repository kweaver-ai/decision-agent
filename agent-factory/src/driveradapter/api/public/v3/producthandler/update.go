package producthandler

import (
	"net/http"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/constant/auditconstant"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/product/productreq"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/capierr"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/capimiddleware"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/chelper"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/cutil"
	"github.com/kweaver-ai/kweaver-go-lib/audit"
	"github.com/kweaver-ai/kweaver-go-lib/rest"
	"github.com/gin-gonic/gin"
)

func (h *productHTTPHandler) Update(c *gin.Context) {
	isPrivate := capimiddleware.IsInternalAPI(c)

	var visitor *rest.Visitor

	if !isPrivate {
		visitor = chelper.GetVisitorFromCtx(c.Request.Context())
	}
	// 1. 获取path参数
	id := c.Param("id")
	if id == "" {
		err := capierr.New400Err(c, "id is empty")
		if !isPrivate {
			audit.NewWarnLogWithError(audit.OPERATION, auditconstant.UPDATE, audit.TransforOperator(*visitor),
				auditconstant.GenerateProductAuditObject("", ""), &err.BaseError)
		}

		_ = c.Error(err)

		return
	}

	// 2. 获取请求体
	var req productreq.UpdateReq

	if err := c.ShouldBindJSON(&req); err != nil {
		httpErr := capierr.New400Err(c, chelper.ErrMsg(err, &req))
		if !isPrivate {
			audit.NewWarnLogWithError(audit.OPERATION, auditconstant.UPDATE, audit.TransforOperator(*visitor),
				auditconstant.GenerateProductAuditObject("", ""), &httpErr.BaseError)
		}

		_ = c.Error(httpErr)

		return
	}

	// 3. 校验请求体
	if err := req.CustomCheck(); err != nil {
		httpErr := capierr.New400Err(c, err.Error())
		if !isPrivate {
			audit.NewWarnLogWithError(audit.OPERATION, auditconstant.UPDATE, audit.TransforOperator(*visitor),
				auditconstant.GenerateProductAuditObject("", ""), &httpErr.BaseError)
		}

		_ = c.Error(httpErr)

		return
	}

	// 4. 调用服务层更新
	auditloginfo, err := h.productService.Update(c, &req, cutil.MustParseInt64(id))
	if err != nil {
		httpErr := capierr.New500Err(c, err.Error())
		if !isPrivate {
			audit.NewWarnLogWithError(audit.OPERATION, auditconstant.UPDATE, audit.TransforOperator(*visitor),
				auditconstant.GenerateProductAuditObject(auditloginfo.ID, auditloginfo.Name), &httpErr.BaseError)
		}

		_ = c.Error(err)

		return
	}

	if !isPrivate {
		audit.NewInfoLog(audit.OPERATION, auditconstant.UPDATE, audit.TransforOperator(*visitor),
			auditconstant.GenerateProductAuditObject(auditloginfo.ID, auditloginfo.Name), "")
	}

	c.Status(http.StatusNoContent)
}
