package spaceresourcedbacc

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
	spaceResourceRepoOnce sync.Once
	spaceResourceRepoImpl idbaccess.ISpaceResourceRepo
)

// SpaceResourceRepo 空间资源仓库实现
type SpaceResourceRepo struct {
	idbaccess.IDBAccBaseRepo

	db *sqlx.DB

	logger icmp.Logger
}

var _ idbaccess.ISpaceResourceRepo = &SpaceResourceRepo{}

func NewSpaceResourceRepo() idbaccess.ISpaceResourceRepo {
	spaceResourceRepoOnce.Do(func() {
		spaceResourceRepoImpl = &SpaceResourceRepo{
			db:             global.GDB,
			logger:         logger.GetLogger(),
			IDBAccBaseRepo: dbaccess.NewDBAccBase(),
		}
	})

	return spaceResourceRepoImpl
}
