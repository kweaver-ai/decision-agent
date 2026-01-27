package conversationsvc

import (
	"context"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/conversation/conversationreq"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/conversation/conversationresp"
	otelHelper "github.com/kweaver-ai/decision-agent/agent-factory/src/infra/opentelemetry"
	otelTrace "github.com/kweaver-ai/decision-agent/agent-factory/src/infra/opentelemetry/trace"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	"github.com/pkg/errors"
)

func (sv *conversationSvc) Init(ctx context.Context, req conversationreq.InitReq) (rt conversationresp.InitConversationResp, err error) {
	ctx, _ = otelTrace.StartInternalSpan(ctx)
	defer otelTrace.EndSpan(ctx, err)

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
		otelHelper.Errorf(ctx, "[Init] create conversation error, err: %v", err)
		return rt, errors.Wrapf(err, "update conversation title failed")
	}

	rt = conversationresp.InitConversationResp{
		ID: po.ID,
	}

	if req.TempareaId != "" {
		err = sv.tempAreaRepo.Bind(ctx, req.TempareaId, po.ID)
		if err != nil {
			otelHelper.Errorf(ctx, "[Init] bind temparea failed, err: %v", err)
			return rt, errors.Wrapf(err, "bind temparea failed")
		}
	}

	return
}
