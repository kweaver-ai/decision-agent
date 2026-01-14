package idatahubacc

import (
	"context"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/httpaccess/datahubcentralhttp/datahubcentraldto"
)

type IDataHubCentral interface {
	CreateDataset(ctx context.Context, req *datahubcentraldto.CreateDatasetsReq) (datasetID string, err error)
}
