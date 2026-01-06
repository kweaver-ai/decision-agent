package idbaccess

import (
	"context"
	"database/sql"

	"github.com/kweaver-ai/proton-rds-sdk-go/sqlx"
)

type IDBAccBaseRepo interface {
	BeginTx(ctx context.Context) (*sql.Tx, error)

	GetDB() *sqlx.DB
}
