package datahubcentraldto

import (
	"fmt"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cutil"
)

type DatasetUpsertRsp struct {
	DatasetID string `json:"dataset_id"`
}

func GetMockDatasetUpsertRspBys() []byte {
	str := fmt.Sprintf(`{
		"dataset_id": "-%s-"
	}`, cutil.UlidMake())

	return []byte(str)
}
