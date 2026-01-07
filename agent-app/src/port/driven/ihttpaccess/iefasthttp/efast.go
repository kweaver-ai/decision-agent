package iefasthttp

import (
	"context"

	"github.com/decision-agent/agent-app/src/drivenadapter/httpaccess/efastaccess/efastdto"
)

type IEfast interface {
	GetObjectFieldByID(ctx context.Context, objectIDs []string, fields ...string) (map[string]*efastdto.DocumentMetaData, error)
}
