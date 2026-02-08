package conversationsvc

import (
	"context"
	"errors"
	"testing"

	"go.uber.org/mock/gomock"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/service"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/idbaccess/idbaccessmock"
	"github.com/stretchr/testify/assert"
)

func TestConversationSvc_Delete_PanicsWithoutConversationRepo(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	svc := &conversationSvc{
		SvcBase: service.NewSvcBase(),
		// conversationRepo is nil
	}

	ctx := context.Background()
	conversationID := "conv-123"

	// This will panic because conversationRepo is nil
	assert.Panics(t, func() {
		_ = svc.Delete(ctx, conversationID)
	})
}

func TestConversationSvc_Delete_WithMockRepo(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockRepo := idbaccessmock.NewMockIConversationRepo(ctrl)

	svc := &conversationSvc{
		SvcBase:          service.NewSvcBase(),
		conversationRepo: mockRepo,
	}

	ctx := context.Background()
	conversationID := "conv-123"

	// Mock the Delete call - gomock Delete method returns (Result, error)
	mockRepo.EXPECT().Delete(ctx, conversationID).Return(int64(0), errors.New("delete error"))

	err := svc.Delete(ctx, conversationID)

	// Should return an error
	assert.Error(t, err)
}
