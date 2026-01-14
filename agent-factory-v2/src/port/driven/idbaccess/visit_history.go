package idbaccess

import (
	"context"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
)

//go:generate mockgen -source=./release.go -destination ./idbaccessmock/release.go -package idbaccessmock
type IVisitHistoryRepo interface {
	IncVisitCount(ctx context.Context, po *dapo.VisitHistoryPO) (err error)
}
