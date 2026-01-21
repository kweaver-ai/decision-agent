package spacememdbacc

import (
	"sync"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/dbaccess"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/cmp/icmp"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/global"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/idbaccess"
	"github.com/kweaver-ai/kweaver-go-lib/logger"

	"github.com/kweaver-ai/proton-rds-sdk-go/sqlx"
)

var (
	spaceMemberRepoOnce sync.Once
	spaceMemberRepoImpl idbaccess.ISpaceMemberRepo
)

// SpaceMemberRepo 空间成员仓库实现
type SpaceMemberRepo struct {
	idbaccess.IDBAccBaseRepo

	db *sqlx.DB

	logger icmp.Logger
}

var _ idbaccess.ISpaceMemberRepo = &SpaceMemberRepo{}

func NewSpaceMemberRepo() idbaccess.ISpaceMemberRepo {
	spaceMemberRepoOnce.Do(func() {
		spaceMemberRepoImpl = &SpaceMemberRepo{
			db:             global.GDB,
			logger:         logger.GetLogger(),
			IDBAccBaseRepo: dbaccess.NewDBAccBase(),
		}
	})

	return spaceMemberRepoImpl
}
