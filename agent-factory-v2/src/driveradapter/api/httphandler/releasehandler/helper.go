package releasehandler

import (
	"github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/release/releasereq"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/chelper"
	"github.com/gin-gonic/gin"
)

func setIsPrivate2Req(c *gin.Context, req *releasereq.PublishReq) {
	isPrivate := chelper.IsInternalAPIFromCtx(c)

	req.IsInternalAPI = isPrivate
}
