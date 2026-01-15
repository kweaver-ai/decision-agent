package afhttpdto

import (
	"errors"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/enum/cdaenum"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/enum/cdapmsenum"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/rdto/agent_permission/cpmsreq"
)

type CheckPmsReq struct {
	// AgentID string `json:"agent_id"`
	ResourceType cdaenum.ResourceType
	ResourceID   string

	Operator cdapmsenum.Operator

	UserID       string `json:"user_id"`
	AppAccountID string `json:"app_account_id"`
}

func (r *CheckPmsReq) IsAgentUseCheck() bool {
	if r.ResourceType == cdaenum.ResourceTypeDataAgent && r.Operator == cdapmsenum.AgentUse {
		return true
	}

	return false
}

func (r *CheckPmsReq) ReqCheck() (err error) {
	if err = r.ResourceType.EnumCheck(); err != nil {
		return
	}

	if err = r.Operator.EnumCheck(); err != nil {
		return
	}

	if r.UserID == "" && r.AppAccountID == "" {
		err = errors.New("[CheckPmsReq][ReqCheck]: req.UserID and req.AppAccountID are both empty")
		return
	}

	if r.ResourceID == "" {
		err = errors.New("[CheckPmsReq][ReqCheck]: req.ResourceID is empty")
		return
	}

	return
}

func NewCheckAgentUsePmsReq(agentID string, userID string, appAccountID string) *CheckPmsReq {
	return &CheckPmsReq{
		ResourceType: cdaenum.ResourceTypeDataAgent,
		ResourceID:   agentID,
		Operator:     cdapmsenum.AgentUse,
		UserID:       userID,
		AppAccountID: appAccountID,
	}
}

func (r *CheckPmsReq) ToCheckPmsReq() (req *cpmsreq.CheckAgentRunReq) {
	req = &cpmsreq.CheckAgentRunReq{}
	req.AgentID = r.ResourceID
	req.UserID = r.UserID
	req.AppAccountID = r.AppAccountID

	return
}
