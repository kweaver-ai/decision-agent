package tempareadbacc

import (
	"sync"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/dbaccess"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/global"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/idbaccess"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/cmp/icmp"
	"github.com/kweaver-ai/kweaver-go-lib/logger"

	"github.com/kweaver-ai/proton-rds-sdk-go/sqlx"
)

var (
	tempAreaRepoOnce sync.Once
	tempAreaRepoImpl idbaccess.ITempAreaRepo
)

type TempAreaRepo struct {
	idbaccess.IDBAccBaseRepo

	db *sqlx.DB

	logger icmp.Logger
}

var _ idbaccess.ITempAreaRepo = &TempAreaRepo{}

func NewTempAreaRepo() idbaccess.ITempAreaRepo {
	tempAreaRepoOnce.Do(func() {
		tempAreaRepoImpl = &TempAreaRepo{
			db:             global.GDB,
			logger:         logger.GetLogger(),
			IDBAccBaseRepo: dbaccess.NewDBAccBase(),
		}
	})

	return tempAreaRepoImpl
}
