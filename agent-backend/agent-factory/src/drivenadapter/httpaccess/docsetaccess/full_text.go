package docsetaccess

import (
	"context"
	"fmt"

	"github.com/bytedance/sonic"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/httpaccess/docsetaccess/docsetdto"
	"github.com/pkg/errors"
	"go.opentelemetry.io/otel/attribute"

	otelHelper "github.com/kweaver-ai/decision-agent/agent-factory/src/infra/opentelemetry"
	otelTrace "github.com/kweaver-ai/decision-agent/agent-factory/src/infra/opentelemetry/trace"
)

func (ds *docsetHttpAcc) FullText(ctx context.Context, req *docsetdto.FullTextReq) (*docsetdto.FullTextRsp, error) {
	var err error

	ctx, _ = otelTrace.StartInternalSpan(ctx)
	defer otelTrace.EndSpan(ctx, err)
	otelTrace.SetAttributes(ctx, attribute.String("doc_id", req.DocID))

	rsp := &docsetdto.FullTextRsp{}
	uri := fmt.Sprintf("%s/api/docset/v1/subdoc/full_text", ds.privateAddress)
	headers := map[string]string{
		"Content-Type": "application/json",
	}

	code, data, err := ds.client.PostNoUnmarshal(ctx, uri, headers, req)
	if err != nil {
		otelHelper.Errorf(ctx, "[FullText] request uri %s err %s,  code %d, resp %s ", uri, err, code, string(data))
		err = errors.Wrapf(err, "request uri %s err %s,  code %d, resp %s ", uri, err, code, string(data))

		return nil, err
	}

	err = sonic.Unmarshal(data, rsp)
	if err != nil {
		otelHelper.Errorf(ctx, "[FullText] request uri %s unmarshal err %s, resp %s ", uri, err, string(data))
		err = errors.Wrapf(err, "request uri %s unmarshal err %s, resp %s ", uri, err, string(data))

		return nil, err
	}

	return rsp, nil
}
