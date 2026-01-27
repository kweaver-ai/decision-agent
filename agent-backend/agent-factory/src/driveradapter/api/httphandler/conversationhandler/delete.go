package conversationhandler

import (
	"fmt"
	"net/http"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/apierr"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/capierr"
	otelHelper "github.com/kweaver-ai/decision-agent/agent-factory/src/infra/opentelemetry"
	"github.com/kweaver-ai/kweaver-go-lib/rest"

	"github.com/gin-gonic/gin"
	"github.com/pkg/errors"
)

func (h *conversationHTTPHandler) Delete(c *gin.Context) {
	// 接收语言标识转换为 context.Context
	ctx := rest.GetLanguageCtx(c)

	id := c.Param("id")
	if id == "" {
		h.logger.Errorf("[Delete] id is empty")
		otelHelper.Error(c, "[Delete] id is empty")
		httpErr := capierr.New400Err(c, "id is empty")
		rest.ReplyError(c, httpErr)

		return
	}

	err := h.conversationSvc.Delete(ctx, id)
	if err != nil {
		h.logger.Errorf("delete conversation failed, cause: %v, err trace: %+v\n", errors.Cause(err), err)
		otelHelper.Error(c, fmt.Sprintf("delete conversation failed, cause: %v, err trace: %+v\n", errors.Cause(err), err))
		// 返回错误
		rest.ReplyError(c, err)

		return
	}

	rest.ReplyOK(c, http.StatusNoContent, "")
}

func (h *conversationHTTPHandler) DeleteByAPPKey(c *gin.Context) {
	// 接收语言标识转换为 context.Context
	ctx := rest.GetLanguageCtx(c)

	appKey := c.Param("app_key")

	if appKey == "" {
		h.logger.Errorf("[DeleteByAPPKey] appKey is empty")
		otelHelper.Error(c, "[DeleteByAPPKey] appKey is empty")
		err := capierr.New400Err(c, "appKey is empty")
		rest.ReplyError(c, err)

		return
	}

	err := h.conversationSvc.DeleteByAppKey(ctx, appKey)
	if err != nil {
		h.logger.Errorf("delete conversation failed, cause: %v, err trace: %+v\n", errors.Cause(err), err)
		otelHelper.Error(c, fmt.Sprintf("delete conversation failed, cause: %v, err trace: %+v\n", errors.Cause(err), err))
		httpErr := rest.NewHTTPError(c.Request.Context(), http.StatusInternalServerError, apierr.ConversationDeleteFailed).WithErrorDetails(fmt.Sprintf("delete conversation failed: %s", err.Error()))
		rest.ReplyError(c, httpErr)

		return
	}

	rest.ReplyOK(c, http.StatusNoContent, "")
}
