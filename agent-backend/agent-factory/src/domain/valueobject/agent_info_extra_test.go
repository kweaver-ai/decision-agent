package valueobject

import (
	"encoding/json"

	"github.com/stretchr/testify/assert"
	"testing"
)

func TestAgentInfo_AdditionalCases(t *testing.T) {
	t.Run("creates AgentInfo with partial values", func(t *testing.T) {
		info := AgentInfo{
			AgentID:     "agent-456",
			AgentName:   "Partial Agent",
			AgentStatus: "inactive",
		}

		assert.Equal(t, "agent-456", info.AgentID)
		assert.Equal(t, "Partial Agent", info.AgentName)
		assert.Equal(t, "inactive", info.AgentStatus)
		assert.Empty(t, info.AgentVersion)
	})

	t.Run("creates AgentInfo pointer", func(t *testing.T) {
		info := &AgentInfo{
			AgentID:      "agent-111",
			AgentName:    "Pointer Agent",
			AgentStatus:  "active",
			AgentVersion: "1.5.0",
		}

		assert.NotNil(t, info)
		assert.Equal(t, "agent-111", info.AgentID)
	})

	t.Run("nil AgentInfo pointer", func(t *testing.T) {
		var info *AgentInfo

		assert.Nil(t, info)
	})
}

func TestAgentInfo_JSON_Additional(t *testing.T) {
	t.Run("unmarshal from JSON with all fields", func(t *testing.T) {
		jsonStr := `{"agent_id":"agent-789","agent_name":"JSON Agent","agent_status":"pending","agent_version":"2.0.0"}`

		var info AgentInfo
		err := json.Unmarshal([]byte(jsonStr), &info)

		assert.NoError(t, err)
		assert.Equal(t, "agent-789", info.AgentID)
		assert.Equal(t, "JSON Agent", info.AgentName)
		assert.Equal(t, "pending", info.AgentStatus)
		assert.Equal(t, "2.0.0", info.AgentVersion)
	})

	t.Run("unmarshal empty JSON", func(t *testing.T) {
		jsonStr := `{}`

		var info AgentInfo
		err := json.Unmarshal([]byte(jsonStr), &info)

		assert.NoError(t, err)
		assert.Empty(t, info.AgentID)
		assert.Empty(t, info.AgentName)
		assert.Empty(t, info.AgentStatus)
		assert.Empty(t, info.AgentVersion)
	})

	t.Run("marshal empty AgentInfo", func(t *testing.T) {
		info := AgentInfo{}

		data, err := json.Marshal(info)
		assert.NoError(t, err)

		expected := `{"agent_id":"","agent_name":"","agent_status":"","agent_version":""}`
		assert.JSONEq(t, expected, string(data))
	})

	t.Run("marshal to JSON with all fields", func(t *testing.T) {
		info := AgentInfo{
			AgentID:      "agent-123",
			AgentName:    "Test Agent",
			AgentStatus:  "active",
			AgentVersion: "1.0.0",
		}

		data, err := json.Marshal(info)
		assert.NoError(t, err)

		expected := `{"agent_id":"agent-123","agent_name":"Test Agent","agent_status":"active","agent_version":"1.0.0"}`
		assert.JSONEq(t, expected, string(data))
	})
}

func TestAgentInfo_SpecialCharacters(t *testing.T) {
	t.Run("agent name with special characters", func(t *testing.T) {
		info := AgentInfo{
			AgentID:      "agent-special",
			AgentName:    "Agent@#$%^&*()",
			AgentStatus:  "active",
			AgentVersion: "1.0.0",
		}

		data, err := json.Marshal(info)
		assert.NoError(t, err)

		var decoded AgentInfo
		err = json.Unmarshal(data, &decoded)
		assert.NoError(t, err)
		assert.Equal(t, info.AgentName, decoded.AgentName)
	})

	t.Run("agent ID with unicode", func(t *testing.T) {
		info := AgentInfo{
			AgentID:      "agent-中文-测试",
			AgentName:    "测试智能体",
			AgentStatus:  "active",
			AgentVersion: "1.0.0",
		}

		data, err := json.Marshal(info)
		assert.NoError(t, err)

		var decoded AgentInfo
		err = json.Unmarshal(data, &decoded)
		assert.NoError(t, err)
		assert.Equal(t, "agent-中文-测试", decoded.AgentID)
		assert.Equal(t, "测试智能体", decoded.AgentName)
	})
}

func TestAgentInfo_CopyByValue(t *testing.T) {
	t.Run("struct copy creates independent instance", func(t *testing.T) {
		original := AgentInfo{
			AgentID:      "agent-999",
			AgentName:    "Original Agent",
			AgentStatus:  "active",
			AgentVersion: "3.0.0",
		}

		copy := original
		copy.AgentName = "Modified Agent"

		assert.NotEqual(t, original.AgentName, copy.AgentName)
		assert.Equal(t, "Original Agent", original.AgentName)
		assert.Equal(t, "Modified Agent", copy.AgentName)
	})
}
