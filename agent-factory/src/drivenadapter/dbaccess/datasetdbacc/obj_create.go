package datasetdbacc

import (
	"context"
	"database/sql"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/enum/daenum"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/types/dto/daconfigdto/dsdto"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/chelper/dbhelper2"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/cutil"
)

func (r *DatasetRepo) CreateDatasetObjs(ctx context.Context, tx *sql.Tx, dto *dsdto.DsComDto, datasetId string) (err error) {
	sr := dbhelper2.TxSr(tx, r.logger)

	objIds := dto.Config.GetBuiltInDocObjIDs()
	objPos := make([]*dapo.DsDatasetObjPo, 0, len(objIds))

	for _, objId := range objIds {
		objPo := &dapo.DsDatasetObjPo{
			DatasetID:  datasetId,
			ObjectID:   objId,
			ObjectType: daenum.DatasetObjTypeDir,
			CreateTime: cutil.GetCurrentMSTimestamp(),
		}

		objPos = append(objPos, objPo)
	}

	_, err = sr.FromPo(&dapo.DsDatasetObjPo{}).
		InsertStructs(objPos)
	if err != nil {
		return
	}

	return
}
