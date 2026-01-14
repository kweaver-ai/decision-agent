package otherhandler

import (
	"net/http"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/enum/cdaenum"
	"github.com/gin-gonic/gin"
)

func (o *otherHTTPHandler) TempZoneFileExt(ctx *gin.Context) {
	fileExtMap := cdaenum.GetFileExtMap()

	ctx.JSON(http.StatusOK, fileExtMap)
}
