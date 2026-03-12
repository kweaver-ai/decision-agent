package conversationmsgdbacc

import (
	"context"
	"database/sql"
	"errors"
	"fmt"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/chelper/dbhelper2"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	o11y "github.com/kweaver-ai/kweaver-go-lib/observability"
	"go.opentelemetry.io/otel/attribute"
)

func (r *ConversationMsgRepo) GetConversationStatus(ctx context.Context, conversationID string) (status string, err error) {
	ctx, _ = o11y.StartInternalSpan(ctx)
	defer o11y.EndSpan(ctx, nil)
	o11y.SetAttributes(ctx, attribute.String("conversationID", conversationID))

	po := &dapo.ConversationMsgPO{}
	sr := dbhelper2.NewSQLRunner(r.db, r.logger)
	sr.FromPo(po)
	sr.Select([]string{"f_status"})
	sr.WhereEqual("f_conversation_id", conversationID)
	sr.WhereEqual("f_is_deleted", 0)
	sr.Order("f_index DESC")
	sr.Limit(1)

	err = sr.FindOne(po)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return "completed", nil
		}
		return "", fmt.Errorf("get conversation status error: %w", err)
	}

	switch po.Status {
	case "failed":
		return "failed", nil
	case "cancelled":
		return "cancelled", nil
	case "processing":
		hasFailed, err := r.hasFailedMessage(ctx, conversationID)
		if err != nil {
			return "", fmt.Errorf("check failed message error: %w", err)
		}
		if hasFailed {
			return "failed", nil
		}
		return "processing", nil
	case "succeded":
		return "completed", nil
	default:
		return "completed", nil
	}
}

func (r *ConversationMsgRepo) hasFailedMessage(ctx context.Context, conversationID string) (bool, error) {
	po := &dapo.ConversationMsgPO{}
	sr := dbhelper2.NewSQLRunner(r.db, r.logger)
	sr.FromPo(po)
	sr.Select([]string{"f_id"})
	sr.WhereEqual("f_conversation_id", conversationID)
	sr.WhereEqual("f_is_deleted", 0)
	sr.WhereEqual("f_status", "failed")
	sr.Limit(1)

	err := sr.FindOne(po)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return false, nil
		}
		return false, fmt.Errorf("check failed message error: %w", err)
	}
	return true, nil
}
