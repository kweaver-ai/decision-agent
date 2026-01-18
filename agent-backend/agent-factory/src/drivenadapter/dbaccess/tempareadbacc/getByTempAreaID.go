package tempareadbacc

import (
	"context"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/chelper/dbhelper2"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cutil"
	"github.com/pkg/errors"
)

// NOTE: 根据临时区域ID获取临时区域文件详情
func (repo *TempAreaRepo) GetByTempAreaID(ctx context.Context, tempAreaID string) (result []*dapo.TempAreaPO, err error) {
	sr := dbhelper2.NewSQLRunner(repo.db, repo.logger)
	sr.FromPo(&dapo.TempAreaPO{})

	poList := make([]dapo.TempAreaPO, 0)

	err = sr.WhereEqual("f_temp_area_id", tempAreaID).Find(&poList)
	if err != nil {
		err = errors.Wrapf(err, "get temp area by temp area id")
		return
	}

	result = cutil.SliceToPtrSlice(poList)

	return
}
