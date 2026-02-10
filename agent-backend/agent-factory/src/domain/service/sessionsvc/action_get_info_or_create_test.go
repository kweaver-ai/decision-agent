package sessionsvc

import (
	"context"
	"testing"

	"go.uber.org/mock/gomock"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/cmp/auditlogcmp"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/session/sessionreq"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/ctype"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/iredisaccess/isessionredis/isessionredismock"
	"github.com/stretchr/testify/assert"
)

func TestHandleGetInfoOrCreate(t *testing.T) {
	t.Run("existing session returns start time and TTL", func(t *testing.T) {
		ctrl := gomock.NewController(t)
		defer ctrl.Finish()

		mockSessionRedis := isessionredismock.NewMockISessionRedisAcc(ctrl)
		mockLogger := auditlogcmp.NewMockLogger(ctrl)
		svc := &sessionSvc{
			sessionRedisAcc: mockSessionRedis,
			logger:          mockLogger,
		}

		ctx := context.Background()
		req := sessionreq.ManageReq{
			ConversationID: "conv-123",
		}
		visitorInfo := &ctype.VisitorInfo{}

		existingStartTime := int64(1234567890)
		existingTTL := 3600

		mockSessionRedis.EXPECT().GetSessionWithTTL(ctx, req.ConversationID).Return(true, existingStartTime, existingTTL, nil)

		startTime, ttl, err := svc.HandleGetInfoOrCreate(ctx, req, visitorInfo, false)

		assert.NoError(t, err)
		assert.Equal(t, existingStartTime, startTime)
		assert.Equal(t, existingTTL, ttl)
	})

	t.Run("creates new session when not exists", func(t *testing.T) {
		ctrl := gomock.NewController(t)
		defer ctrl.Finish()

		mockSessionRedis := isessionredismock.NewMockISessionRedisAcc(ctrl)
		mockLogger := auditlogcmp.NewMockLogger(ctrl)
		svc := &sessionSvc{
			sessionRedisAcc: mockSessionRedis,
			logger:          mockLogger,
		}

		ctx := context.Background()
		req := sessionreq.ManageReq{
			ConversationID: "new-conv",
		}
		visitorInfo := &ctype.VisitorInfo{}

		mockSessionRedis.EXPECT().GetSessionWithTTL(ctx, req.ConversationID).Return(false, 0, 0, nil)
		mockSessionRedis.EXPECT().SetSession(ctx, req.ConversationID, gomock.Any(), gomock.Any()).Return(nil)
		mockSessionRedis.EXPECT().GetSessionTTL(ctx, req.ConversationID).Return(3600, nil)

		startTime, ttl, err := svc.HandleGetInfoOrCreate(ctx, req, visitorInfo, false)

		assert.NoError(t, err)
		assert.NotZero(t, startTime)
		assert.NotZero(t, ttl)
	})

	t.Run("returns error when get session fails", func(t *testing.T) {
		ctrl := gomock.NewController(t)
		defer ctrl.Finish()

		mockSessionRedis := isessionredismock.NewMockISessionRedisAcc(ctrl)
		mockLogger := auditlogcmp.NewMockLogger(ctrl)
		svc := &sessionSvc{
			sessionRedisAcc: mockSessionRedis,
			logger:          mockLogger,
		}

		ctx := context.Background()
		req := sessionreq.ManageReq{
			ConversationID: "conv-123",
		}
		visitorInfo := &ctype.VisitorInfo{}

		expectedErr := assert.AnError
		mockSessionRedis.EXPECT().GetSessionWithTTL(ctx, req.ConversationID).Return(false, 0, 0, expectedErr)
		mockLogger.EXPECT().Errorf(gomock.Any(), gomock.Any(), gomock.Any()).AnyTimes()

		startTime, ttl, err := svc.HandleGetInfoOrCreate(ctx, req, visitorInfo, false)

		assert.Error(t, err)
		assert.Zero(t, startTime)
		assert.Zero(t, ttl)
	})

	t.Run("returns error when set session fails", func(t *testing.T) {
		ctrl := gomock.NewController(t)
		defer ctrl.Finish()

		mockSessionRedis := isessionredismock.NewMockISessionRedisAcc(ctrl)
		mockLogger := auditlogcmp.NewMockLogger(ctrl)
		svc := &sessionSvc{
			sessionRedisAcc: mockSessionRedis,
			logger:          mockLogger,
		}

		ctx := context.Background()
		req := sessionreq.ManageReq{
			ConversationID: "new-conv",
		}
		visitorInfo := &ctype.VisitorInfo{}

		mockSessionRedis.EXPECT().GetSessionWithTTL(ctx, req.ConversationID).Return(false, 0, 0, nil)
		expectedErr := assert.AnError
		mockSessionRedis.EXPECT().SetSession(ctx, req.ConversationID, gomock.Any(), gomock.Any()).Return(expectedErr)
		mockLogger.EXPECT().Errorf(gomock.Any(), gomock.Any(), gomock.Any()).AnyTimes()

		startTime, ttl, err := svc.HandleGetInfoOrCreate(ctx, req, visitorInfo, false)

		assert.Error(t, err)
		assert.Zero(t, startTime)
		assert.Zero(t, ttl)
	})

	t.Run("returns error when get TTL after create fails", func(t *testing.T) {
		ctrl := gomock.NewController(t)
		defer ctrl.Finish()

		mockSessionRedis := isessionredismock.NewMockISessionRedisAcc(ctrl)
		mockLogger := auditlogcmp.NewMockLogger(ctrl)
		svc := &sessionSvc{
			sessionRedisAcc: mockSessionRedis,
			logger:          mockLogger,
		}

		ctx := context.Background()
		req := sessionreq.ManageReq{
			ConversationID: "new-conv",
		}
		visitorInfo := &ctype.VisitorInfo{}

		mockSessionRedis.EXPECT().GetSessionWithTTL(ctx, req.ConversationID).Return(false, 0, 0, nil)
		mockSessionRedis.EXPECT().SetSession(ctx, req.ConversationID, gomock.Any(), gomock.Any()).Return(nil)
		expectedErr := assert.AnError
		mockSessionRedis.EXPECT().GetSessionTTL(ctx, req.ConversationID).Return(0, expectedErr)
		mockLogger.EXPECT().Errorf(gomock.Any(), gomock.Any(), gomock.Any()).AnyTimes()

		startTime, ttl, err := svc.HandleGetInfoOrCreate(ctx, req, visitorInfo, false)

		assert.Error(t, err)
		assert.Zero(t, startTime)
		assert.Zero(t, ttl)
	})

	t.Run("nil service causes panic", func(t *testing.T) {
		var svc *sessionSvc
		ctx := context.Background()
		req := sessionreq.ManageReq{
			ConversationID: "conv-123",
		}
		visitorInfo := &ctype.VisitorInfo{}

		// This will panic when trying to use sessionRedisAcc
		assert.Panics(t, func() {
			svc.HandleGetInfoOrCreate(ctx, req, visitorInfo, false)
		})
	})

	t.Run("nil session redis causes panic", func(t *testing.T) {
		svc := &sessionSvc{
			// sessionRedisAcc is nil, will panic
		}
		ctx := context.Background()
		req := sessionreq.ManageReq{
			ConversationID: "conv-123",
		}
		visitorInfo := &ctype.VisitorInfo{}

		// This will panic when trying to use sessionRedisAcc
		assert.Panics(t, func() {
			svc.HandleGetInfoOrCreate(ctx, req, visitorInfo, false)
		})
	})
}

