package idbaccess

import (
	"context"
	"database/sql"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/valueobject/spacevo"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/space/spacereq"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
)

//go:generate mockgen -package idbaccessmock -destination ./idbaccessmock/space_repo.go github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/idbaccess ISpaceRepo

// ISpaceRepo 空间仓库接口
type ISpaceRepo interface {
	IDBAccBaseRepo

	Create(ctx context.Context, tx *sql.Tx, id string, po *dapo.SpacePo) (err error)
	Update(ctx context.Context, tx *sql.Tx, po *dapo.SpacePo) (err error)
	Delete(ctx context.Context, tx *sql.Tx, id string) (err error)

	ExistsByName(ctx context.Context, name string) (exists bool, err error)
	ExistsByKey(ctx context.Context, key string) (exists bool, err error)

	ExistsByID(ctx context.Context, id string) (exists bool, err error)
	ExistsByNameExcludeID(ctx context.Context, name, id string) (exists bool, err error)

	GetByID(ctx context.Context, id string) (po *dapo.SpacePo, err error)

	List(ctx context.Context, req *spacereq.ListReq) (pos []*dapo.SpacePo, count int64, err error)

	GetSpacePosByMembers(ctx context.Context, tx *sql.Tx, members []*spacevo.MemberUniq, req *spacereq.ListReq) (pos []*dapo.SpacePo, count int64, err error)
}
