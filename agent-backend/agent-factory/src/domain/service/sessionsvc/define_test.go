package sessionsvc

import (
	"testing"

	"go.uber.org/mock/gomock"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/iredisaccess/isessionredis/isessionredismock"
	"github.com/stretchr/testify/assert"
)

func TestNewSessionService(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	dto := &NewSessionSvcDto{
		SessionRedis: isessionredismock.NewMockISessionRedisAcc(ctrl),
	}

	svc := NewSessionService(dto)

	assert.NotNil(t, svc)
}

func TestNewSessionService_WithLogger(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	dto := &NewSessionSvcDto{
		Logger:       nil,
		SessionRedis: isessionredismock.NewMockISessionRedisAcc(ctrl),
	}

	svc := NewSessionService(dto)

	assert.NotNil(t, svc)
	assert.IsType(t, &sessionSvc{}, svc)
}
