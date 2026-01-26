package agentsvc

import (
	"testing"

	agentreq "github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/agent/req"
	"github.com/stretchr/testify/assert"
)

func TestBuildUserQuery(t *testing.T) {
	tests := []struct {
		name           string
		originalQuery  string
		conversationID string
		selectedFiles  []agentreq.SelectedFile
		expectedPrefix string
		expectedQuery  string
	}{
		{
			name:           "no files selected",
			originalQuery:  "hello",
			conversationID: "conv-123",
			selectedFiles:  []agentreq.SelectedFile{},
			expectedPrefix: "hello",
			expectedQuery:  "hello",
		},
		{
			name:           "single file selected",
			originalQuery:  "analyze data",
			conversationID: "conv-123",
			selectedFiles: []agentreq.SelectedFile{
				{FileName: "data.csv"},
			},
			expectedPrefix: "当前会话的临时文件路径：/workspace/conv-123/uploads/temparea/\n\n可用文件：\n- data.csv (/workspace/conv-123/uploads/temparea/data.csv)\n\n用户问题：analyze data",
			expectedQuery:  "当前会话的临时文件路径：/workspace/conv-123/uploads/temparea/\n\n可用文件：\n- data.csv (/workspace/conv-123/uploads/temparea/data.csv)\n\n用户问题：analyze data",
		},
		{
			name:           "multiple files selected",
			originalQuery:  "compare files",
			conversationID: "conv-456",
			selectedFiles: []agentreq.SelectedFile{
				{FileName: "data1.csv"},
				{FileName: "data2.csv"},
				{FileName: "config.json"},
			},
			expectedPrefix: "当前会话的临时文件路径：/workspace/conv-456/uploads/temparea/",
		},
		{
			name:           "empty query with files",
			originalQuery:  "",
			conversationID: "conv-789",
			selectedFiles: []agentreq.SelectedFile{
				{FileName: "test.csv"},
			},
			expectedPrefix: "当前会话的临时文件路径：/workspace/conv-789/uploads/temparea/\n\n可用文件：\n- test.csv (/workspace/conv-789/uploads/temparea/test.csv)\n\n用户问题：",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := buildUserQuery(tt.originalQuery, tt.conversationID, tt.selectedFiles)
			assert.Contains(t, result, tt.expectedPrefix)
		})
	}
}
