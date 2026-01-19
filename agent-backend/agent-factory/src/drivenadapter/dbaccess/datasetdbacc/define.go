package datasetdbacc

import (
	"sync"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/dbaccess"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/idbaccess"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/cmp/icmp"
	"github.com/kweaver-ai/kweaver-go-lib/logger"
)

var (
	datasetRepoOnce sync.Once
	datasetRepoImpl idbaccess.IDatasetRepo
)

type DatasetRepo struct {
	idbaccess.IDBAccBaseRepo

	logger icmp.Logger
}

var _ idbaccess.IDatasetRepo = &DatasetRepo{}

func NewDatasetRepo() idbaccess.IDatasetRepo {
	datasetRepoOnce.Do(func() {
		datasetRepoImpl = &DatasetRepo{
			logger:         logger.GetLogger(),
			IDBAccBaseRepo: dbaccess.NewDBAccBase(),
		}
	})

	return datasetRepoImpl
}
