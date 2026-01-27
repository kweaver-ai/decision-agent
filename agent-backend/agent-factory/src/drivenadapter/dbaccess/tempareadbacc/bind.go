package tempareadbacc

import (
	"context"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/chelper/dbhelper2"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	otelTrace "github.com/kweaver-ai/decision-agent/agent-factory/src/infra/opentelemetry/trace"
	"go.opentelemetry.io/otel/attribute"
)

func (repo *TempAreaRepo) Bind(ctx context.Context, areaID string, conversationID string) error {
	ctx, _ = otelTrace.StartInternalSpan(ctx)
	defer otelTrace.EndSpan(ctx, nil)
	otelTrace.SetAttributes(ctx, attribute.String("areaID", areaID))
	otelTrace.SetAttributes(ctx, attribute.String("conversationID", conversationID))

	sr := dbhelper2.NewSQLRunner(repo.db, repo.logger)
	po := &dapo.TempAreaPO{}
	sr.FromPo(po)
	_, err := sr.WhereEqual("f_temp_area_id", areaID).Update(map[string]interface{}{"f_conversation_id": conversationID})

	return err
}
