package datahubcentralhttp

import (
	"context"
	"fmt"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/httpaccess/datahubcentralhttp/datahubcentraldto"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/chelper/cenvhelper"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/chelper/httphelper"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cutil"
	"github.com/pkg/errors"
)

func (e *dataHubHttpAcc) CreateDataset(ctx context.Context, req *datahubcentraldto.CreateDatasetsReq) (datasetID string, err error) {
	uri := fmt.Sprintf("%s%s", e.privateAddress, datasetsPath)

	var bys []byte
	if cenvhelper.IsAaronLocalDev() {
		// 这里是为了本地开发使用的
		bys = datahubcentraldto.GetMockDatasetUpsertRspBys()
		err = nil
	} else {
		c := httphelper.NewHTTPClient()
		bys, err = c.PostJSONExpect2xxByte(ctx, uri, req)
	}

	if err != nil {
		err = errors.Wrapf(err, "[dataHubHttpAcc][CreateDataset] request uri %s err %s", uri, err)
		e.logger.Errorln(err)

		return
	}

	info := &datahubcentraldto.DatasetUpsertRsp{}

	err = cutil.JSON().Unmarshal(bys, info)
	if err != nil {
		err = errors.Wrapf(err, "[dataHubHttpAcc][CreateDataset] unmarshal rsp err %s", err)
		e.logger.Errorln(err)

		return
	}

	datasetID = info.DatasetID

	return
}
