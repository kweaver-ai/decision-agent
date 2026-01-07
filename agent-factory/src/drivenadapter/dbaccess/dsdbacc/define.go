package dsdbacc

import (
	"sync"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/dbaccess/datasetdbacc"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/global"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/idbaccess"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/cmp/icmp"
	"github.com/kweaver-ai/kweaver-go-lib/logger"

	"github.com/kweaver-ai/proton-rds-sdk-go/sqlx"
)

var (
	dsRepoOnce sync.Once
	dsRepoImpl idbaccess.IDsRepo
)

type DsRepo struct {
	*drivenadapter.RepoBase

	db *sqlx.DB

	logger icmp.Logger

	datasetRepo idbaccess.IDatasetRepo
}

var _ idbaccess.IDsRepo = &DsRepo{}

func NewDsRepo() idbaccess.IDsRepo {
	dsRepoOnce.Do(func() {
		dsRepoImpl = &DsRepo{
			db:          global.GDB,
			logger:      logger.GetLogger(),
			RepoBase:    drivenadapter.NewRepoBase(),
			datasetRepo: datasetdbacc.NewDatasetRepo(),
		}
	})

	return dsRepoImpl
}
