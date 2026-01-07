package conversationdbacc

import (
	"context"

	"github.com/kweaver-ai/decision-agent/agent-app/src/infra/persistence/dapo"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/chelper/dbhelper2"
	o11y "github.com/kweaver-ai/kweaver-go-lib/observability"
	"go.opentelemetry.io/otel/attribute"
)

// GetByID implements idbaccess.IConversationRepo.
func (repo *ConversationRepo) GetByID(ctx context.Context, id string) (po *dapo.ConversationPO, err error) {
	ctx, _ = o11y.StartInternalSpan(ctx)
	defer o11y.EndSpan(ctx, nil)
	o11y.SetAttributes(ctx, attribute.String("conversationID", id))

	po = &dapo.ConversationPO{}
	sr := dbhelper2.NewSQLRunner(repo.db, repo.logger)
	sr.FromPo(po)
	err = sr.WhereEqual("f_id", id).WhereEqual("f_is_deleted", 0).FindOne(po)

	return
}
