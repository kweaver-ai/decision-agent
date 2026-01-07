package iportdriver

import (
	"context"

	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/driveradapter/api/rdto/session/sessionreq"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/driveradapter/api/rdto/session/sessionresp"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-go-common-pkg/src/infra/common/ctype"
)

//go:generate mockgen -source=./session_svc.go -destination ./iportdrivermock/session_svc.go -package iportdrivermock
type ISessionSvc interface {
	Manage(ctx context.Context, req sessionreq.ManageReq, visitorInfo *ctype.VisitorInfo) (resp sessionresp.ManageResp, err error)
	HandleGetInfoOrCreate(ctx context.Context, req sessionreq.ManageReq, visitorInfo *ctype.VisitorInfo, isTriggerCacheUpsert bool) (startTime int64, ttl int, err error)
	HandleRecoverLifetimeOrCreate(ctx context.Context, req sessionreq.ManageReq, visitorInfo *ctype.VisitorInfo, isTriggerCacheUpsert bool) (startTime int64, ttl int, err error)
}
