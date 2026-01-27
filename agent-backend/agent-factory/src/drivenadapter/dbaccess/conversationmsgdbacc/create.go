package conversationmsgdbacc

import (
	"context"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/chelper/dbhelper2"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cutil"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	otelTrace "github.com/kweaver-ai/decision-agent/agent-factory/src/infra/opentelemetry/trace"
	"go.opentelemetry.io/otel/attribute"
)

// Create implements idbaccess.IConversationMsgRepo.
func (repo *ConversationMsgRepo) Create(ctx context.Context, po *dapo.ConversationMsgPO) (id string, err error) {
	ctx, _ = otelTrace.StartInternalSpan(ctx)
	defer otelTrace.EndSpan(ctx, nil)
	otelTrace.SetAttributes(ctx, attribute.String("conversationID", po.ConversationID))
	po.ID = cutil.UlidMake()
	po.CreateTime = cutil.GetCurrentMSTimestamp()
	po.UpdateTime = po.CreateTime
	sr := dbhelper2.NewSQLRunner(repo.db, repo.logger)

	sr.FromPo(po)
	_, err = sr.InsertStruct(po)

	return po.ID, err
}
