package tempareadbacc

import (
	"context"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/chelper/dbhelper2"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
)

func (repo *TempAreaRepo) Create(ctx context.Context, po []*dapo.TempAreaPO) (err error) {
	sr := dbhelper2.NewSQLRunner(repo.db, repo.logger)
	sr.FromPo(&dapo.TempAreaPO{})
	_, err = sr.InsertStructs(po)

	return
}
