package datasetdbacc

import (
	"context"
	"database/sql"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/chelper/dbhelper2"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
)

func (r *DatasetRepo) DeleteDatasetAndObj(ctx context.Context, tx *sql.Tx, datasetId string) (err error) {
	// 1. delete dataset
	sr := dbhelper2.TxSr(tx, r.logger)

	_, err = sr.FromPo(&dapo.DsDatasetPo{}).
		WhereEqual("f_id", datasetId).
		Delete()
	if err != nil {
		return
	}

	// 2. delete dataset obj
	err = r.DeleteObj(tx, datasetId)

	return
}
