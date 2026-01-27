package agentfactoryaccess

import (
	"context"
	"fmt"
	"net/http"

	"github.com/bytedance/sonic"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/httpaccess/agentfactoryaccess/agentfactorydto"
	"github.com/pkg/errors"
	"go.opentelemetry.io/otel/attribute"

	otelHelper "github.com/kweaver-ai/decision-agent/agent-factory/src/infra/opentelemetry"
	otelTrace "github.com/kweaver-ai/decision-agent/agent-factory/src/infra/opentelemetry/trace"
)

type ErrResponse struct {
	Description string `json:"Description"`
	ErrorCode   string `json:"ErrorCode"`
}

func (af *agentFactoryHttpAcc) GetAgent(ctx context.Context, agentID string, version string) (agentfactorydto.Agent, error) {
	var err error

	ctx, _ = otelTrace.StartInternalSpan(ctx)
	defer otelTrace.EndSpan(ctx, err)
	otelTrace.SetAttributes(ctx, attribute.String("agent_id", agentID))
	otelTrace.SetAttributes(ctx, attribute.String("version", version))

	agent := agentfactorydto.Agent{}

	uri := fmt.Sprintf("%s/api/agent-factory/internal/v3/agent-market/agent/%s/version/%s", af.privateAddress, agentID, version)
	code, res, err := af.client.GetNoUnmarshal(ctx, uri, nil, nil)

	if err != nil {
		otelHelper.Errorf(ctx, "[GetAgent] request uri %s err %s", uri, err)
		err = errors.Wrapf(err, "[GetAgent] request uri %s err %s", uri, err)

		return agent, err
	}

	if code != http.StatusOK {
		otelHelper.Errorf(ctx, "[GetAgent] status code: %d , resp %s", code, string(res))
		return agent, fmt.Errorf("status code: %d , resp %s", code, string(res))
	}

	err = sonic.Unmarshal(res, &agent)
	if err != nil {
		otelHelper.Errorf(ctx, "[GetAgent] request uri %s unmarshal err %s,  resp %s ", uri, err, string(res))
		return agent, errors.Wrapf(err, "[GetAgent] request uri %s unmarshal err %s,  resp %s ", uri, err, string(res))
	}

	return agent, nil
}
