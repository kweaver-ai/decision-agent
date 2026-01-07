package sessionhandler

import (
	"fmt"
	"net/http"

	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/driveradapter/api/rdto/session/sessionreq"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-go-common-pkg/src/infra/common/capierr"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-go-common-pkg/src/infra/common/cenum"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-go-common-pkg/src/infra/common/chelper"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-go-common-pkg/src/infra/common/ctype"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/mdl-go-lib/rest"
	"github.com/gin-gonic/gin"
)

func (h *sessionHTTPHandler) Manage(c *gin.Context) {
	// 1. 获取请求参数
	var req sessionreq.ManageReq

	if err := c.ShouldBindJSON(&req); err != nil {
		httpErr := capierr.New400Err(c, chelper.ErrMsg(err, &req))
		rest.ReplyError(c, httpErr)

		return
	}

	// 获取path参数
	req.ConversationID = c.Param("conversation_id")
	if req.ConversationID == "" {
		httpErr := capierr.New400Err(c, "conversation_id不能为空")
		rest.ReplyError(c, httpErr)

		return
	}

	// 2. 获取visitor信息
	visitor := chelper.GetVisitorFromCtx(c)
	if visitor == nil {
		httpErr := capierr.New401Err(c, "[Manage] visitor not found")
		rest.ReplyError(c, httpErr)

		return
	}

	visitorInfo := &ctype.VisitorInfo{
		XBusinessDomainID: cenum.BizDomainID(chelper.GetBizDomainIDFromCtx(c)),
	}
	visitorInfo.XAccountID = visitor.ID
	visitorInfo.XAccountType.LoadFromMDLVisitorType(visitor.Type)

	// 3. 调用service
	resp, err := h.sessionSvc.Manage(c.Request.Context(), req, visitorInfo)
	if err != nil {
		errMsg := fmt.Sprintf("[sessionHTTPHandler][Manage] failed to manage session: %v", err)

		h.logger.Errorf(errMsg)

		httpErr := capierr.New500Err(c, errMsg)

		rest.ReplyError(c, httpErr)

		return
	}

	// 4. 返回结果
	rest.ReplyOK(c, http.StatusOK, resp)
}
