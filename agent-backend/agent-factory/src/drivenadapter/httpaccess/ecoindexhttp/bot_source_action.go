package ecoindexhttp

import (
	"context"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/valueobject/daconfvalobj/datasourcevalobj"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/chelper/cenvhelper"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/chelper/httphelper"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cutil"
	"github.com/pkg/errors"
)

type ActionReqItem struct {
	BotRev     string `json:"bot_rev"`
	Source     string `json:"source"`
	SourceType string `json:"source_type"`
	ActionType string `json:"type"`
}

func (e *ecoIndexHttpAcc) AddBotSourceIndex(ctx context.Context, uniqueFlag string, sources []*datasourcevalobj.DocSourceField) (err error) {
	return e.botSourceAction(ctx, uniqueFlag, sources, actionAddIndex)
}

func (e *ecoIndexHttpAcc) RemoveSourceIndex(ctx context.Context, uniqueFlag string, sources []*datasourcevalobj.DocSourceField) (err error) {
	return e.botSourceAction(ctx, uniqueFlag, sources, actionRemoveIndex)
}

func (e *ecoIndexHttpAcc) botSourceAction(ctx context.Context, uniqueFlag string, sources []*datasourcevalobj.DocSourceField, action string) (err error) {
	var req []*ActionReqItem

	for _, source := range sources {
		sourceValue := source.GetDirObjID()
		if sourceValue != "" {
			item := &ActionReqItem{
				BotRev:     uniqueFlag,
				Source:     sourceValue,
				ActionType: action,
				SourceType: "doc",
			}

			req = append(req, item)
		}
	}

	uri := e.privateAddress + bindBotPath

	if cenvhelper.IsAaronLocalDev() {
		err = nil
	} else {
		c := httphelper.NewHTTPClient()
		_, err = c.PostJSONExpect2xx(ctx, uri, req)
	}

	if err != nil {
		d, _ := cutil.JSON().Marshal(req)
		err = errors.Wrapf(err, "[ecoIndexHttpAcc][botSourceAction] request uri %s data %s", uri, string(d))
		e.logger.Errorln(err)

		return
	}

	return
}
