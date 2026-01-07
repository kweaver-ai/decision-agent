package datasetdbacc

import (
	"context"
	"database/sql"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/dbaccess/dbacccom"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/chelper/dbhelper2"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/cutil"
)

func (r *DatasetRepo) Create(ctx context.Context, tx *sql.Tx, id, hashSha256 string) (err error) {
	sr := dbhelper2.TxSr(tx, r.logger)

	// id, err = r.getUniqID(ctx, tx)
	//if err != nil {
	//	return
	//}

	po := &dapo.DsDatasetPo{
		ID:         id,
		HashSha256: hashSha256,
		CreateTime: cutil.GetCurrentMSTimestamp(),
	}

	_, err = sr.FromPo(po).
		InsertStruct(po)
	if err != nil {
		return
	}

	return
}

func (r *DatasetRepo) getUniqID(ctx context.Context, tx *sql.Tx) (id string, err error) {
	h := dbacccom.NewUniqUlidHelper(&dbacccom.UniqUlidHelper{
		Po:     &dapo.DsDatasetPo{},
		Pk:     "f_id",
		Tx:     tx,
		Logger: r.logger,
	})

	id, err = h.GenDBID(ctx)

	return
}
