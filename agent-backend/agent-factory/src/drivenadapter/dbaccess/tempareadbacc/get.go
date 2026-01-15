package tempareadbacc

import (
	"context"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/chelper/dbhelper2"
	o11y "github.com/kweaver-ai/kweaver-go-lib/observability"
	"go.opentelemetry.io/otel/attribute"
)

func (repo *TempAreaRepo) GetByConversationID(ctx context.Context, conversationID string) (po *dapo.TempAreaPO, err error) {
	ctx, _ = o11y.StartInternalSpan(ctx)
	defer o11y.EndSpan(ctx, nil)
	o11y.SetAttributes(ctx, attribute.String("conversationID", conversationID))

	po = &dapo.TempAreaPO{}
	sr := dbhelper2.NewSQLRunner(repo.db, repo.logger)
	sr.FromPo(po)
	err = sr.WhereEqual("f_conversation_id", conversationID).FindOne(po)

	return
}
