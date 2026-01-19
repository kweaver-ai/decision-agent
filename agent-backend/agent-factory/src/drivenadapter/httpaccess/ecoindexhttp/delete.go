package ecoindexhttp

import (
	"context"
	"fmt"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/chelper/httphelper"
)

func (e *ecoIndexHttpAcc) DeleteBotIndex(ctx context.Context, botID string) (err error) {
	uri := fmt.Sprintf("%s%s/%s", e.privateAddress, bindBotPath, botID)

	c := httphelper.NewHTTPClient()
	_, err = c.DeleteExpect2xx(ctx, uri)

	if err != nil {
		e.logger.Errorf("[DeleteBotIndex] request uri %s err %s", uri, err)
	}

	return
}
