package conversationmsgdbacc

import (
	"context"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/chelper/dbhelper2"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	otelTrace "github.com/kweaver-ai/decision-agent/agent-factory/src/infra/opentelemetry/trace"
	"go.opentelemetry.io/otel/attribute"
)

// Update implements idbaccess.IConversationMsgRepo.
func (repo *ConversationMsgRepo) Update(ctx context.Context, po *dapo.ConversationMsgPO) (err error) {
	ctx, _ = otelTrace.StartInternalSpan(ctx)
	defer otelTrace.EndSpan(ctx, nil)
	otelTrace.SetAttributes(ctx, attribute.String("conversationID", po.ConversationID))
	otelTrace.SetAttributes(ctx, attribute.String("msgID", po.ID))

	sr := dbhelper2.NewSQLRunner(repo.db, repo.logger)

	sr.FromPo(po)

	_, err = sr.WhereEqual("f_id", po.ID).
		SetUpdateFields([]string{
			"f_content",
			"f_content_type",
			"f_status",
			"f_ext",
			"f_update_time",
			"f_update_by",
		}).
		UpdateByStruct(po)

	return
}
