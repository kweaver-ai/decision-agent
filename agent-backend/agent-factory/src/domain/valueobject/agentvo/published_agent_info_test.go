package agentvo

import (
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/enum/cdaenum"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestNewPublishedAgentInfo(t *testing.T) {
	info := NewPublishedAgentInfo()
	assert.NotNil(t, info)
	assert.Empty(t, info.PublishedBy)
	assert.Empty(t, info.PublishedByName)
	assert.Equal(t, int64(0), info.PublishedAt)
	assert.Empty(t, info.Profile)
	assert.Empty(t, info.Version)
	assert.Empty(t, info.Avatar)
}

func TestPublishedAgentInfo_LoadFromReleaseAgentPO(t *testing.T) {
	tests := []struct {
		name    string
		po      *dapo.PublishedJoinPo
		wantErr bool
		checkInfo func(t *testing.T, info *PublishedAgentInfo)
	}{
		{
			name: "valid published agent po",
			po: &dapo.PublishedJoinPo{
				ReleasePartPo: dapo.ReleasePartPo{
					ReleaseID:    "release-1",
					PublishDesc:   "Test publish",
					Version:       "v1.0.0",
					PublishedAt:    1000000,
					PublishedBy:    "user-1",
					IsPmsCtrl:      1,
					PublishedToBeStruct: dapo.PublishedToBeStruct{
						IsAPIAgent:      1,
						IsWebSDKAgent:   0,
						IsSkillAgent:    1,
						IsDataFlowAgent: 0,
					},
				},
				DataAgentPo: dapo.DataAgentPo{
					ID:         "agent-1",
					Name:       "Test Agent",
					Profile:    strPtr("Test profile"),
					AvatarType: cdaenum.AvatarTypeBuiltIn,
					Avatar:     "🤖",
				},
			},
			wantErr: false,
			checkInfo: func(t *testing.T, info *PublishedAgentInfo) {
				assert.NotNil(t, info)
				assert.Equal(t, "user-1", info.PublishedBy)
				assert.Equal(t, int64(1000000), info.PublishedAt)
				assert.Equal(t, "v1.0.0", info.Version)
				assert.Equal(t, "Test profile", info.Profile)
				assert.Equal(t, "🤖", info.Avatar)
				assert.Equal(t, cdaenum.AvatarTypeBuiltIn, info.AvatarType)
				assert.Equal(t, 1, info.IsAPIAgent)
				assert.Equal(t, 0, info.IsWebSDKAgent)
				assert.Equal(t, 1, info.IsSkillAgent)
			},
		},
		{
			name: "minimal published agent po",
			po: &dapo.PublishedJoinPo{
				ReleasePartPo: dapo.ReleasePartPo{
					ReleaseID:  "release-2",
					PublishedAt: 2000000,
					PublishedBy: "user-2",
				},
			},
			wantErr: false,
			checkInfo: func(t *testing.T, info *PublishedAgentInfo) {
				assert.NotNil(t, info)
				assert.Equal(t, "user-2", info.PublishedBy)
				assert.Equal(t, int64(2000000), info.PublishedAt)
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			info := NewPublishedAgentInfo()
			err := info.LoadFromReleaseAgentPO(tt.po)
			if tt.wantErr {
				require.Error(t, err)
			} else {
				require.NoError(t, err)
				if tt.checkInfo != nil {
					tt.checkInfo(t, info)
				}
			}
		})
	}
}

func TestPublishedAgentInfo_Fields(t *testing.T) {
	info := &PublishedAgentInfo{
		PublishedBy:      "user-1",
		PublishedByName:  "User One",
		PublishedAt:      1000000,
		Profile:         "Agent profile",
		Version:         "v1.0",
		AvatarType:       cdaenum.AvatarTypeUserUploaded,
		Avatar:           "custom.png",
		PublishedToBeStruct: dapo.PublishedToBeStruct{
			IsAPIAgent:      1,
			IsWebSDKAgent:   1,
			IsSkillAgent:    0,
			IsDataFlowAgent: 1,
		},
	}

	assert.Equal(t, "user-1", info.PublishedBy)
	assert.Equal(t, "User One", info.PublishedByName)
	assert.Equal(t, int64(1000000), info.PublishedAt)
	assert.Equal(t, "Agent profile", info.Profile)
	assert.Equal(t, "v1.0", info.Version)
	assert.Equal(t, "custom.png", info.Avatar)
	assert.Equal(t, cdaenum.AvatarTypeUserUploaded, info.AvatarType)
	assert.Equal(t, 1, info.IsAPIAgent)
	assert.Equal(t, 1, info.IsWebSDKAgent)
	assert.Equal(t, 0, info.IsSkillAgent)
	assert.Equal(t, 1, info.IsDataFlowAgent)
}

func TestPublishUserInfo(t *testing.T) {
	info := &PublishUserInfo{
		UserID:   "user-123",
		Username: "testuser",
	}

	assert.Equal(t, "user-123", info.UserID)
	assert.Equal(t, "testuser", info.Username)
}

// Helper function
func strPtr(s string) *string {
	return &s
}
