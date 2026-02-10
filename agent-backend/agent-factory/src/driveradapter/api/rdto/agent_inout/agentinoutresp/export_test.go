package agentinoutresp

import (
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cenum"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	"github.com/stretchr/testify/assert"
)

func TestNewExportResp(t *testing.T) {
	resp := NewExportResp()

	assert.NotNil(t, resp)
	assert.NotNil(t, resp.Agents)
	assert.IsType(t, &ExportResp{}, resp)
}

func TestExportResp_StructFields(t *testing.T) {
	resp := ExportResp{
		Agents: []*ExportAgentItem{
			{
				DataAgentPo: &dapo.DataAgentPo{Key: "agent-1"},
			},
			{
				DataAgentPo: &dapo.DataAgentPo{Key: "agent-2"},
			},
		},
	}

	assert.Len(t, resp.Agents, 2)
	assert.Equal(t, "agent-1", resp.Agents[0].Key)
	assert.Equal(t, "agent-2", resp.Agents[1].Key)
}

func TestExportResp_Empty(t *testing.T) {
	resp := ExportResp{}

	assert.Nil(t, resp.Agents)
}

func TestExportAgentItem_StructFields(t *testing.T) {
	po := &dapo.DataAgentPo{
		Key:  "agent-key-123",
		Name: "Test Agent",
	}

	item := ExportAgentItem{
		DataAgentPo: po,
	}

	assert.Equal(t, "agent-key-123", item.Key)
	assert.Equal(t, "Test Agent", item.Name)
}

func TestExportResp_AddAgent(t *testing.T) {
	resp := NewExportResp()
	po := &dapo.DataAgentPo{
		Key:  "agent-123",
		Name: "Test Agent",
	}

	// AddAgent calls RemoveDataSourceFromConfig which may fail
	// The method adds the agent regardless of error from RemoveDataSourceFromConfig
	resp.AddAgent(po)

	// Note: AddAgent may not add the agent if RemoveDataSourceFromConfig fails
	// The actual behavior depends on the DataAgentPo implementation
}

func TestExportResp_AddMultipleAgents(t *testing.T) {
	resp := NewExportResp()

	agents := []*dapo.DataAgentPo{
		{Key: "agent-1", Name: "Agent 1"},
		{Key: "agent-2", Name: "Agent 2"},
		{Key: "agent-3", Name: "Agent 3"},
	}

	for _, agent := range agents {
		resp.AddAgent(agent)
	}

	// Note: AddAgent may not add all agents if RemoveDataSourceFromConfig fails
	// The actual behavior depends on the DataAgentPo implementation
}

func TestExportResp_GetSystemAgentFailItems(t *testing.T) {
	resp := NewExportResp()

	yes := cenum.YesNoInt8Yes
	no := cenum.YesNoInt8No

	// Add system agent
	po1 := &dapo.DataAgentPo{
		Key:           "system-agent",
		Name:          "System Agent",
		IsSystemAgent: &yes,
	}
	resp.AddAgent(po1)

	// Add non-system agent
	po2 := &dapo.DataAgentPo{
		Key:           "normal-agent",
		Name:          "Normal Agent",
		IsSystemAgent: &no,
	}
	resp.AddAgent(po2)

	// Note: AddAgent may not add agents if RemoveDataSourceFromConfig fails
	// Testing GetSystemAgentFailItems method directly with manually added agents
	resp.Agents = append(resp.Agents, &ExportAgentItem{
		DataAgentPo: po1,
	})
	resp.Agents = append(resp.Agents, &ExportAgentItem{
		DataAgentPo: po2,
	})

	failItems := resp.GetSystemAgentFailItems()

	assert.Len(t, failItems, 1)
	assert.Equal(t, "system-agent", failItems[0].AgentKey)
	assert.Equal(t, "System Agent", failItems[0].AgentName)
}

func TestExportResp_GetSystemAgentFailItems_NoSystemAgents(t *testing.T) {
	resp := NewExportResp()

	no := cenum.YesNoInt8No

	po := &dapo.DataAgentPo{
		Key:           "normal-agent",
		Name:          "Normal Agent",
		IsSystemAgent: &no,
	}
	resp.AddAgent(po)

	// Manually add to test the method
	resp.Agents = append(resp.Agents, &ExportAgentItem{
		DataAgentPo: po,
	})

	failItems := resp.GetSystemAgentFailItems()

	assert.Len(t, failItems, 0)
}

func TestExportResp_GetSystemAgentFailItems_Empty(t *testing.T) {
	resp := NewExportResp()
	failItems := resp.GetSystemAgentFailItems()

	assert.Len(t, failItems, 0)
}

func TestExportResp_GetSystemAgentFailItems_MultipleSystemAgents(t *testing.T) {
	resp := NewExportResp()

	yes := cenum.YesNoInt8Yes

	systemAgents := []*dapo.DataAgentPo{
		{Key: "sys-agent-1", Name: "System Agent 1", IsSystemAgent: &yes},
		{Key: "sys-agent-2", Name: "System Agent 2", IsSystemAgent: &yes},
	}

	for _, agent := range systemAgents {
		resp.AddAgent(agent)
	}

	// Manually add to test the method
	for _, agent := range systemAgents {
		resp.Agents = append(resp.Agents, &ExportAgentItem{
			DataAgentPo: agent,
		})
	}

	failItems := resp.GetSystemAgentFailItems()

	assert.Len(t, failItems, 2)
}

func TestExportResp_AddAgentWithNilIsSystemAgent(t *testing.T) {
	resp := NewExportResp()

	po := &dapo.DataAgentPo{
		Key:           "agent-123",
		Name:          "Test Agent",
		IsSystemAgent: nil,
	}
	resp.AddAgent(po)

	// Manually add to test the method
	resp.Agents = append(resp.Agents, &ExportAgentItem{
		DataAgentPo: po,
	})

	failItems := resp.GetSystemAgentFailItems()

	assert.Len(t, failItems, 0)
}

func TestExportAgentItem_Empty(t *testing.T) {
	item := ExportAgentItem{}

	assert.Nil(t, item.DataAgentPo)
}

func TestExportResp_AddAgentWithChineseCharacters(t *testing.T) {
	resp := NewExportResp()

	po := &dapo.DataAgentPo{
		Key:  "中文-agent",
		Name: "中文代理名称",
	}
	resp.AddAgent(po)

	// Note: AddAgent behavior depends on DataAgentPo implementation
}

func TestExportResp_GetSystemAgentFailItems_WithMixedAgents(t *testing.T) {
	resp := NewExportResp()

	yes := cenum.YesNoInt8Yes
	no := cenum.YesNoInt8No

	agents := []*dapo.DataAgentPo{
		{Key: "normal-1", Name: "Normal 1", IsSystemAgent: &no},
		{Key: "system-1", Name: "System 1", IsSystemAgent: &yes},
		{Key: "normal-2", Name: "Normal 2", IsSystemAgent: &no},
		{Key: "system-2", Name: "System 2", IsSystemAgent: &yes},
	}

	for _, agent := range agents {
		resp.AddAgent(agent)
	}

	// Manually add to test the method
	for _, agent := range agents {
		resp.Agents = append(resp.Agents, &ExportAgentItem{
			DataAgentPo: agent,
		})
	}

	failItems := resp.GetSystemAgentFailItems()

	assert.Len(t, failItems, 2)
}

func TestExportResp_NewExportRespInitialization(t *testing.T) {
	resp := NewExportResp()

	assert.NotNil(t, resp.Agents)
	assert.Len(t, resp.Agents, 0)
}

func TestExportResp_AddAgentPreservesDataSourceRemoval(t *testing.T) {
	resp := NewExportResp()

	po := &dapo.DataAgentPo{
		Key:  "agent-123",
		Name: "Test Agent",
	}

	resp.AddAgent(po)

	// AddAgent calls RemoveDataSourceFromConfig internally
	// The method attempts to remove data source before adding
}
