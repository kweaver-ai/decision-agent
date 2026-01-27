package tempareadbacc

import (
	"context"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/chelper/dbhelper2"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	otelTrace "github.com/kweaver-ai/decision-agent/agent-factory/src/infra/opentelemetry/trace"
	"go.opentelemetry.io/otel/attribute"
)

func (repo *TempAreaRepo) GetByConversationID(ctx context.Context, conversationID string) (po *dapo.TempAreaPO, err error) {
	ctx, _ = otelTrace.StartInternalSpan(ctx)
	defer otelTrace.EndSpan(ctx, nil)
	otelTrace.SetAttributes(ctx, attribute.String("conversationID", conversationID))

	po = &dapo.TempAreaPO{}
	sr := dbhelper2.NewSQLRunner(repo.db, repo.logger)
	sr.FromPo(po)
	err = sr.WhereEqual("f_conversation_id", conversationID).FindOne(po)

	return
}
