package spaceresourcedbacc

import (
	"context"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/dbaccess/spacedb/spaceresourcedbacc/srdbarg"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/chelper/dbhelper2"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/chelper/sqlhelper2"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/cutil"
)

// List 获取空间资源列表
func (repo *SpaceResourceRepo) List(ctx context.Context, arg *srdbarg.GetSRListArg) (rt []*dapo.SpaceResourcePo, err error) {
	// 使用新的SQLRunner进行Find查询
	poList := make([]dapo.SpaceResourcePo, 0)

	findSr := dbhelper2.NewSQLRunner(repo.db, repo.logger)

	findSr.FromPo(&dapo.SpaceResourcePo{}).
		WhereEqual("f_space_id", arg.SpaceID)

	if arg.ResourceType != "" {
		findSr.WhereEqual("f_resource_type", arg.ResourceType)
	}

	if arg.PageByIntID != nil {
		if arg.PageByIntID.Size > 0 {
			findSr.Limit(arg.PageByIntID.Size)
		}

		if arg.PageByIntID.LastID > 0 {
			findSr.Where("f_id", sqlhelper2.OperatorLt, arg.PageByIntID.LastID)
		}
	}

	err = findSr.Order("f_id DESC").Find(&poList)
	if err != nil {
		return
	}

	rt = cutil.SliceToPtrSlice(poList)

	return
}
