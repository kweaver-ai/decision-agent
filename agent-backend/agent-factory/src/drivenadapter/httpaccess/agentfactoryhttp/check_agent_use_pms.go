package agentfactoryhttp

import (
	"context"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/httpaccess/agentfactoryhttp/afhttpdto"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/rdto/agent_permission/cpmsresp"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cenum"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/chelper"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/chelper/httphelper"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cutil"
	"github.com/pkg/errors"
)

func (a *agentFactoryHttpAcc) CheckAgentUsePermission(ctx context.Context, req *afhttpdto.CheckPmsReq) (ok bool, err error) {
	if !req.IsAgentUseCheck() {
		err = errors.New("agentFactoryHttpAcc.CheckAgentUsePermission: req is not agent use check")
		return
	}

	_req := req.ToCheckPmsReq()

	url := a.privateBaseURL + "/api/agent-factory/internal/v3/agent-permission/execute"

	// 根据 UserID 和 AppAccountID 设置 x-account 相关 Header
	headerMap := make(map[string]string)
	if req.UserID != "" {
		chelper.SetAccountInfoToHeaderMap(headerMap, req.UserID, cenum.AccountTypeUser)
	} else if req.AppAccountID != "" {
		chelper.SetAccountInfoToHeaderMap(headerMap, req.AppAccountID, cenum.AccountTypeApp)
	}

	c := httphelper.NewHTTPClient(httphelper.WithHeaders(headerMap))

	respBody, err := c.PostJSONExpect2xxByte(ctx, url, _req)
	if err != nil {
		chelper.RecordErrLogWithPos(a.logger, err, "agentFactoryHttpAcc.CheckAgentUsePermission http post")
		err = errors.Wrap(err, "发送HTTP请求失败")

		return
	}

	resp := &cpmsresp.CheckRunResp{}

	err = cutil.JSON().Unmarshal(respBody, resp)
	if err != nil {
		chelper.RecordErrLogWithPos(a.logger, err, "agentFactoryHttpAcc.CheckAgentUsePermission unmarshal response")
		err = errors.Wrap(err, "解析响应数据失败")

		return
	}

	ok = resp.IsAllowed

	return
}
