package publishedtpldbacc

import (
	"context"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/chelper/dbhelper2"
)

func (repo *PubedTplRepo) ExistsByKey(ctx context.Context, key string) (exists bool, err error) {
	po := &dapo.PublishedTplPo{}
	sr := dbhelper2.NewSQLRunner(repo.db, repo.logger)
	sr.FromPo(po)

	count, err := sr.
		WhereEqual("f_key", key).
		Count()
	if err != nil {
		return false, err
	}

	return count > 0, nil
}

func (repo *PubedTplRepo) ExistsByID(ctx context.Context, id int64) (exists bool, err error) {
	po := &dapo.PublishedTplPo{}
	sr := dbhelper2.NewSQLRunner(repo.db, repo.logger)
	sr.FromPo(po)

	count, err := sr.
		WhereEqual("f_id", id).
		Count()
	if err != nil {
		return false, err
	}

	return count > 0, nil
}
