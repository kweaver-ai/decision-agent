package agentsvc

import (
	"testing"

	agentreq "github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/agent/req"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/service/util"
	"github.com/stretchr/testify/assert"
)

func TestBuildWorkspaceContextMessage(t *testing.T) {
	tests := []struct {
		name            string
		conversationID  string
		userID          string
		selectedFiles   []agentreq.SelectedFile
		expectedPrefix  string
		expectedContent string
	}{
		{
			name:           "no files selected",
			conversationID: "conv-123",
			userID:         "user-123",
			selectedFiles:  []agentreq.SelectedFile{},
			expectedPrefix: "",
		},
		{
			name:           "single file selected",
			conversationID: "conv-123",
			userID:         "user-456",
			selectedFiles: []agentreq.SelectedFile{
				{FileName: "/workspace/conv-123/uploads/temparea/data.csv"},
			},
			expectedPrefix:  "【System auto-generated context - not user query】",
			expectedContent: "- data.csv (/workspace/conv-123/uploads/temparea/data.csv)",
		},
		{
			name:           "multiple files selected",
			conversationID: "conv-456",
			userID:         "user-789",
			selectedFiles: []agentreq.SelectedFile{
				{FileName: "/workspace/conv-456/uploads/temparea/data1.csv"},
				{FileName: "/workspace/conv-456/uploads/temparea/data2.csv"},
				{FileName: "/workspace/conv-456/uploads/temparea/config.json"},
			},
			expectedPrefix: "【System auto-generated context - not user query】",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := util.BuildWorkspaceContextMessage(tt.conversationID, tt.userID, tt.selectedFiles)
			if tt.expectedPrefix == "" {
				assert.Empty(t, result)
			} else {
				assert.Contains(t, result, tt.expectedPrefix)
			}
			if tt.expectedContent != "" {
				assert.Contains(t, result, tt.expectedContent)
			}
		})
	}
}
