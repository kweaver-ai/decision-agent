package valueobject

import (
	"testing"
)

func TestAgentInfo(t *testing.T) {
	agent := &AgentInfo{
		AgentID:      "12345",
		AgentName:    "Test Agent",
		AgentStatus:  "active",
		AgentVersion: "1.0.0",
	}

	if agent.AgentID != "12345" {
		t.Errorf("AgentID = %q, want %q", agent.AgentID, "12345")
	}
	if agent.AgentName != "Test Agent" {
		t.Errorf("AgentName = %q, want %q", agent.AgentName, "Test Agent")
	}
	if agent.AgentStatus != "active" {
		t.Errorf("AgentStatus = %q, want %q", agent.AgentStatus, "active")
	}
	if agent.AgentVersion != "1.0.0" {
		t.Errorf("AgentVersion = %q, want %q", agent.AgentVersion, "1.0.0")
	}
}

func TestAgentInfo_Empty(t *testing.T) {
	agent := &AgentInfo{}

	if agent.AgentID != "" {
		t.Errorf("AgentID should be empty")
	}
	if agent.AgentName != "" {
		t.Errorf("AgentName should be empty")
	}
}
