package iecoConfighttp

import (
	"context"

	"github.com/kweaver-ai/decision-agent/agent-app/src/drivenadapter/httpaccess/ecoconfigaccess/ecoconfigdto"
)

type IEcoConfig interface {
	DocReindex(ctx context.Context, request []ecoconfigdto.ReindexReq) (err error)
}
