package idbaccess

import (
	"context"
	"database/sql"

	"github.com/kweaver-ai/proton-rds-sdk-go/sqlx"
)

//go:generate mockgen -source=./base.go -destination ./idbaccessmock/base.go -package idbaccessmock
type IDBAccBaseRepo interface {
	BeginTx(ctx context.Context) (*sql.Tx, error)

	GetDB() *sqlx.DB
}
