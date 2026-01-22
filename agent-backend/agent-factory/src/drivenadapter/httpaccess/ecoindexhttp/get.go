package ecoindexhttp

import (
	"context"
	"fmt"
	"net/url"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/valueobject/comvalobj"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/httpaccess/ecoindexhttp/ecoindexdto"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/chelper/cenvhelper"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/chelper/httphelper"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cutil"
	"github.com/pkg/errors"
)

func (e *ecoIndexHttpAcc) GetBotIndexStatus(ctx context.Context, uniqueFlag string, showFailInfos bool, failInfoPagination *comvalobj.Pagination) (info *ecoindexdto.BotIndexStatusInfo, err error) {
	vals := url.Values{}
	vals.Add("fail_infos", fmt.Sprintf("%t", showFailInfos))
	vals.Add("limit", fmt.Sprint(failInfoPagination.Limit))
	vals.Add("offset", fmt.Sprint(failInfoPagination.Offset))

	uri := fmt.Sprintf("%s%s/%s?%s", e.privateAddress, bindBotPath, uniqueFlag, vals.Encode())

	var bys []byte
	if cenvhelper.IsAaronLocalDev() {
		// 这里是为了本地开发使用的
		bys = ecoindexdto.GetMockBotIndexStatusInfoBys()
		err = nil
	} else {
		c := httphelper.NewHTTPClient()
		bys, err = c.GetExpect2xxByte(ctx, uri, nil)
	}

	if err != nil {
		err = errors.Wrapf(err, "[ecoIndexHttpAcc][GetBotIndexStatus] request uri %s err %s", uri, err)
		e.logger.Errorln(err)

		return
	}

	info = &ecoindexdto.BotIndexStatusInfo{}

	err = cutil.JSON().Unmarshal(bys, info)
	if err != nil {
		err = errors.Wrapf(err, "[ecoIndexHttpAcc][GetBotIndexStatus] unmarshal rsp err %s", err)
		e.logger.Errorln(err)

		return
	}

	info.BotVersion = uniqueFlag

	return
}
