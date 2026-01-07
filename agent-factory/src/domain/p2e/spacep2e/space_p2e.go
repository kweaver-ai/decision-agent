package spacep2e

import (
	"context"

	"github.com/kweaver-ai/decision-agent/agent-factory/locale"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/entity/spaceeo"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/cmp/umcmp/dto/umarg"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/cmp/umcmp/umtypes"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/chelper/cenvhelper"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/cutil"
	"github.com/kweaver-ai/agent-go-common-pkg/src/port/driven/ihttpaccess/iumacc"
)

// Space PO转EO
func Space(ctx context.Context, _po *dapo.SpacePo) (eo *spaceeo.Space, err error) {
	eo = &spaceeo.Space{}

	err = cutil.CopyStructUseJSON(&eo.SpacePo, _po)
	if err != nil {
		return
	}

	return
}

// Spaces 批量PO转EO
func Spaces(ctx context.Context, _pos []*dapo.SpacePo, umHttp iumacc.UmHttpAcc) (eos []*spaceeo.Space, err error) {
	eos = make([]*spaceeo.Space, 0, len(_pos))

	userIDs := make([]string, 0, len(_pos))
	for i := range _pos {
		userIDs = append(userIDs, _pos[i].CreatedBy)
		userIDs = append(userIDs, _pos[i].UpdatedBy)
	}

	arg := &umarg.GetOsnArgDto{
		UserIDs: userIDs,
	}

	ret := umtypes.NewOsnInfoMapS()

	if cenvhelper.IsLocalDev() {
		// 本地开发环境模拟数据
		for _, userID := range arg.UserIDs {
			ret.UserNameMap[userID] = userID + "_name"
		}
	} else {
		ret, err = umHttp.GetOsnNames(ctx, arg)
		if err != nil {
			return
		}
	}

	unknownUserName := locale.GetI18nByCtx(ctx, locale.UnknownUser)

	for i := range _pos {
		var eo *spaceeo.Space

		if eo, err = Space(ctx, _pos[i]); err != nil {
			return
		}

		if eo.CreatedBy != "" {
			userName, ok := ret.UserNameMap[eo.CreatedBy]
			if !ok {
				userName = unknownUserName
			}

			eo.CreatedByName = userName
		}

		if eo.UpdatedBy != "" {
			userName, ok := ret.UserNameMap[eo.UpdatedBy]
			if !ok {
				userName = unknownUserName
			}

			eo.UpdatedByName = userName
		}

		eos = append(eos, eo)
	}

	return
}
