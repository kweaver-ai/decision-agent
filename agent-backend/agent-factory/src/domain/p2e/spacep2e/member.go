package spacep2e

import (
	"context"

	"github.com/kweaver-ai/decision-agent/agent-factory/locale"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/entity/spaceeo"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/cmp/umcmp/dto/umarg"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/cmp/umcmp/umtypes"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cenum"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/chelper/cenvhelper"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cutil"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/ihttpaccess/iumacc"
)

// SpaceMember PO转EO
func SpaceMember(ctx context.Context, _po *dapo.SpaceMemberPo) (eo *spaceeo.SpaceMember, err error) {
	eo = &spaceeo.SpaceMember{}

	err = cutil.CopyStructUseJSON(&eo.SpaceMemberPo, _po)
	if err != nil {
		return
	}

	return
}

// SpaceMembers 批量PO转EO
func SpaceMembers(ctx context.Context, _pos []*dapo.SpaceMemberPo, umHttp iumacc.UmHttpAcc) (eos []*spaceeo.SpaceMember, err error) {
	eos = make([]*spaceeo.SpaceMember, 0, len(_pos))

	// 1. 构建umHttp参数
	arg := &umarg.GetOsnArgDto{
		UserIDs:       []string{},
		DepartmentIDs: []string{},
		GroupIDs:      []string{},
	}

	for i := range _pos {
		switch _pos[i].ObjType {
		case cenum.OrgObjTypeUser:
			arg.UserIDs = append(arg.UserIDs, _pos[i].ObjID)
		case cenum.OrgObjTypeDep:
			arg.DepartmentIDs = append(arg.DepartmentIDs, _pos[i].ObjID)
		case cenum.OrgObjTypeGroup:
			arg.GroupIDs = append(arg.GroupIDs, _pos[i].ObjID)
		}
	}

	ret := umtypes.NewOsnInfoMapS()

	if cenvhelper.IsLocalDev() {
		// 本地开发环境模拟数据
		for _, userID := range arg.UserIDs {
			ret.UserNameMap[userID] = userID + "_name"
		}

		for _, depID := range arg.DepartmentIDs {
			ret.DepartmentNameMap[depID] = depID + "_name"
		}

		for _, groupID := range arg.GroupIDs {
			ret.GroupNameMap[groupID] = groupID + "_name"
		}
	} else {
		ret, err = umHttp.GetOsnNames(ctx, arg)
		if err != nil {
			return
		}
	}

	unknownUserName := locale.GetI18nByCtx(ctx, locale.UnknownUser)

	// 2. 转换为EO
	for i := range _pos {
		var eo *spaceeo.SpaceMember

		if eo, err = SpaceMember(ctx, _pos[i]); err != nil {
			return
		}

		switch _pos[i].ObjType {
		case cenum.OrgObjTypeUser:
			userName, ok := ret.UserNameMap[_pos[i].ObjID]
			if !ok {
				userName = unknownUserName
			}

			eo.ObjName = userName
		case cenum.OrgObjTypeDep:
			eo.ObjName = ret.DepartmentNameMap[_pos[i].ObjID]
		case cenum.OrgObjTypeGroup:
			eo.ObjName = ret.GroupNameMap[_pos[i].ObjID]
		}

		eos = append(eos, eo)
	}

	return
}
