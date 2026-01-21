package spacedbacc

import (
	"context"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/chelper/dbhelper2"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
)

// GetByID 根据ID获取空间
func (repo *SpaceRepo) GetByID(ctx context.Context, id string) (po *dapo.SpacePo, err error) {
	po = &dapo.SpacePo{}
	sr := dbhelper2.NewSQLRunner(repo.db, repo.logger)
	sr.FromPo(po)
	err = sr.WhereEqual("f_id", id).
		WhereEqual("f_deleted_at", 0).
		FindOne(po)

	return
}
