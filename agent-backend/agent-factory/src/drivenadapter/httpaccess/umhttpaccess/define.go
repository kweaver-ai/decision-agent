package umhttpaccess

import (
	"context"

	"github.com/kweaver-ai/decision-agent/agent-factory/cconf"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/cmp/icmp"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/cmp/umcmp"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/cmp/umcmp/dto/umarg"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/cmp/umcmp/umtypes"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cglobal"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/ihttpaccess/iumacc"
)

// umClient abstracts the methods used from umcmp.Um for testability.
type umClient interface {
	GetOsnNamesSFG(ctx context.Context, args *umarg.GetOsnArgDto) (ret *umtypes.OsnInfoMapS, err error)
	GetUserDeptIDs(ctx context.Context, userID string) (deptIDs []string, err error)
	GetDeptInfoMap(ctx context.Context, args *umarg.GetDeptInfoArgDto) (dim map[string]*umtypes.DepartmentInfo, err error)
	GetUserDept(ctx context.Context, userID string) (depts [][]umcmp.ObjectBaseInfo, err error)
	GetUserInfo(ctx context.Context, args *umarg.GetUserInfoArgDto) (uim umcmp.UserInfoMap, err error)
}

type umHttpAcc struct {
	um     umClient
	logger icmp.Logger
}

var _ iumacc.UmHttpAcc = &umHttpAcc{}

func NewUmHttpAcc(
	logger icmp.Logger,
) iumacc.UmHttpAcc {
	umConf := &cconf.UserMgntCfg{
		Host:     cglobal.GConfig.Hydra.UserMgnt.Host,
		Port:     cglobal.GConfig.Hydra.UserMgnt.Port,
		Protocol: "http",
	}

	_um := umcmp.NewUmCmp(
		umConf,
		logger,
	)

	umImpl := &umHttpAcc{
		um:     _um,
		logger: logger,
	}

	return umImpl
}
