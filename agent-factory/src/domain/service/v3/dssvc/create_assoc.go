package dssvc

import (
	"context"
	"database/sql"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/types/dto/daconfigdto/dsdto"
)

// CreateAssocOnly 只创建assoc，不创建dataset obj等
func (s *dsSvc) CreateAssocOnly(ctx context.Context, tx *sql.Tx, dto *dsdto.DsUniqDto, datasetId string) (err error) {
	_, err = s.dsRepo.Create(ctx, tx, dto, datasetId)
	if err != nil {
		return
	}

	return
}
