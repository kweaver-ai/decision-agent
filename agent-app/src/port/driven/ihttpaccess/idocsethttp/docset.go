package idocsethttp

import (
	"context"

	"github.com/data-agent/agent-app/src/drivenadapter/httpaccess/docsetaccess/docsetdto"
)

type IDocset interface {
	FullText(ctx context.Context, req *docsetdto.FullTextReq) (rsp *docsetdto.FullTextRsp, err error)
}
