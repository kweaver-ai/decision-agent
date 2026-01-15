package tempareadbacc

import (
	"context"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/chelper/dbhelper2"
	o11y "github.com/kweaver-ai/kweaver-go-lib/observability"
	"go.opentelemetry.io/otel/attribute"
)

func (repo *TempAreaRepo) Bind(ctx context.Context, areaID string, conversationID string) error {
	ctx, _ = o11y.StartInternalSpan(ctx)
	defer o11y.EndSpan(ctx, nil)
	o11y.SetAttributes(ctx, attribute.String("areaID", areaID))
	o11y.SetAttributes(ctx, attribute.String("conversationID", conversationID))

	sr := dbhelper2.NewSQLRunner(repo.db, repo.logger)
	po := &dapo.TempAreaPO{}
	sr.FromPo(po)
	_, err := sr.WhereEqual("f_temp_area_id", areaID).Update(map[string]interface{}{"f_conversation_id": conversationID})

	return err
}
