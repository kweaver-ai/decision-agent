package comvalobj

import (
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/constant/cdaconstant"
	"github.com/stretchr/testify/assert"
)

func TestDataAgentUniqFlag_ValObjCheck(t *testing.T) {
	tests := []struct {
		name    string
		flag    *DataAgentUniqFlag
		wantErr bool
	}{
		{
			name: "完整配置",
			flag: NewDataAgentUniqFlag("agent-123", "v1.0"),
			wantErr: false,
		},
		{
			name: "缺少AgentID",
			flag: &DataAgentUniqFlag{
				AgentVersion: "v1.0",
			},
			wantErr: true,
		},
		{
			name: "缺少AgentVersion",
			flag: &DataAgentUniqFlag{
				AgentID: "agent-123",
			},
			wantErr: true,
		},
		{
			name: "两者都为空",
			flag: &DataAgentUniqFlag{
				AgentID:     "",
				AgentVersion: "",
			},
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := tt.flag.ValObjCheck()
			if tt.wantErr {
				assert.Error(t, err, "expected error")
			} else {
				assert.NoError(t, err, "expected no error")
			}
		})
	}
}

func TestDataAgentUniqFlag_NewDataAgentUniqFlag(t *testing.T) {
	flag := NewDataAgentUniqFlag("test-id", "v1.0")
	if flag.AgentID != "test-id" {
		t.Errorf("AgentID = %s, want test-id", flag.AgentID)
	}
	if flag.AgentVersion != "v1.0" {
		t.Errorf("AgentVersion = %s, want v1.0", flag.AgentVersion)
	}
}

func TestDataAgentUniqFlag_IsUnpublish(t *testing.T) {
	tests := []struct {
		name     string
		flag     *DataAgentUniqFlag
		expected bool
	}{
		{
			name: "未发布版本",
			flag: &DataAgentUniqFlag{
				AgentID:      "agent-123",
				AgentVersion: "v1.0",
			},
			expected: false,
		},
		{
			name: "发布版本",
			flag: &DataAgentUniqFlag{
				AgentID:      "agent-123",
				AgentVersion: cdaconstant.AgentVersionUnpublished,
			},
			expected: true,
		},
		{
			name: "其他版本",
			flag: &DataAgentUniqFlag{
				AgentID:      "agent-123",
				AgentVersion: "v2.0",
			},
			expected: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := tt.flag.IsUnpublish()
			assert.Equal(t, tt.expected, got, "IsUnpublish() should match expected")
		})
	}
}
