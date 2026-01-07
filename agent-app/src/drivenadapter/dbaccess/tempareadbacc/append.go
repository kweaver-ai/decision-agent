package tempareadbacc

import (
	"context"

	"github.com/decision-agent/agent-app/src/infra/persistence/dapo"
)

func (repo *TempAreaRepo) Append(ctx context.Context, po []*dapo.TempAreaPO) (err error) {
	return
}
