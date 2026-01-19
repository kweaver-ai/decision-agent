package tempareasvc

import (
	"context"

	tempareareq "github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/temparea/req"
	"github.com/pkg/errors"
)

func (svc *tempareaSvc) Remove(ctx context.Context, req tempareareq.RemoveReq) (err error) {
	err = svc.tempAreaRepo.Remove(ctx, req.TempAreaID, req.SourceIDs)
	if err != nil {
		return errors.Wrap(err, "remove temp area failed")
	}

	return nil
}
