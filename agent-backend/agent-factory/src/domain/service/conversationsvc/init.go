package conversationsvc

import (
	"context"
	"fmt"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/conversation/conversationreq"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/conversation/conversationresp"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	o11y "github.com/kweaver-ai/kweaver-go-lib/observability"
	"github.com/pkg/errors"
)

func (sv *conversationSvc) Init(ctx context.Context, req conversationreq.InitReq) (rt conversationresp.InitConversationResp, err error) {
	ctx, _ = o11y.StartInternalSpan(ctx)
	defer o11y.EndSpan(ctx, err)

	if req.Title == "" {
		req.Title = "新会话"
	}

	po := &dapo.ConversationPO{
		AgentAPPKey: req.AgentAPPKey,
		CreateBy:    req.UserID,
		UpdateBy:    req.UserID,
		Title:       req.Title,
		Ext:         new(string),
	}

	po, err = sv.conversationRepo.Create(ctx, po)
	if err != nil {
		o11y.Error(ctx, fmt.Sprintf("[Init] create conversation error, err: %v", err))
		return rt, errors.Wrapf(err, "update conversation title failed")
	}

	rt = conversationresp.InitConversationResp{
		ID: po.ID,
	}

	return
}
