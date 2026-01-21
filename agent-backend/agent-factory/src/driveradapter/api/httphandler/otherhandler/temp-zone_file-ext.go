package otherhandler

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/enum/cdaenum"
)

func (o *otherHTTPHandler) TempZoneFileExt(ctx *gin.Context) {
	fileExtMap := cdaenum.GetFileExtMap()

	ctx.JSON(http.StatusOK, fileExtMap)
}
