package conversationsvc

import (
	"context"
	"testing"

	agentreq "github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/agent/req"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	"github.com/stretchr/testify/assert"
)

func TestBuildWorkspaceContextMessage_AdditionalCases(t *testing.T) {
	tests := []struct {
		name          string
		conversationID string
		userID        string
		selectedFiles []agentreq.SelectedFile
		wantContains  []string
		wantEmpty     bool
	}{
		{
			name:           "nil selected files",
			conversationID: "conv-123",
			userID:         "user-456",
			selectedFiles:  nil,
			wantEmpty:      true,
		},
		{
			name:           "multiple files",
			conversationID: "conv-123",
			userID:         "user-456",
			selectedFiles: []agentreq.SelectedFile{
				{FileName: "/workspace/conv-123/uploads/temparea/data1.csv"},
				{FileName: "/workspace/conv-123/uploads/temparea/data2.csv"},
			},
			wantContains: []string{
				"sess-user-456",
				"data1.csv",
				"data2.csv",
			},
		},
		{
			name:           "file with different path structure",
			conversationID: "conv-abc",
			userID:         "user-xyz",
			selectedFiles: []agentreq.SelectedFile{
				{FileName: "/different/path/file.txt"},
			},
			wantContains: []string{
				"sess-user-xyz",
			},
		},
		{
			name:           "file with matching path",
			conversationID: "conv-test",
			userID:         "user-001",
			selectedFiles: []agentreq.SelectedFile{
				{FileName: "/workspace/conv-test/uploads/temparea/test.json"},
			},
			wantContains: []string{
				"sess-user-001",
				"test.json",
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := buildWorkspaceContextMessage(tt.conversationID, tt.userID, tt.selectedFiles)

			if tt.wantEmpty {
				assert.Empty(t, result)
			} else {
				for _, substr := range tt.wantContains {
					assert.Contains(t, result, substr)
				}
			}
		})
	}
}

func TestGetID_AdditionalCases(t *testing.T) {
	ctx := context.Background()

	t.Run("messages with reply IDs", func(t *testing.T) {
		messages := []*dapo.ConversationMsgPO{
			{ID: "msg1", Role: "user", ReplyID: "msg2"},
			{ID: "msg2", Role: "assistant"},
		}

		userMsgID, assistantMsgID := GetID(ctx, messages, "msg1", "")

		assert.Equal(t, "msg1", userMsgID)
		assert.Equal(t, "msg2", assistantMsgID)
	})

	t.Run("last message is user", func(t *testing.T) {
		messages := []*dapo.ConversationMsgPO{
			{ID: "msg1", Role: "user"},
			{ID: "msg2", Role: "assistant"},
			{ID: "msg3", Role: "user"},
		}

		userMsgID, assistantMsgID := GetID(ctx, messages, "msg1", "")

		assert.Equal(t, "msg1", userMsgID)
		assert.Equal(t, "msg2", assistantMsgID)
	})

	t.Run("empty messages slice", func(t *testing.T) {
		messages := []*dapo.ConversationMsgPO{}

		userMsgID, assistantMsgID := GetID(ctx, messages, "", "")

		assert.Empty(t, userMsgID)
		assert.Empty(t, assistantMsgID)
	})
}

func TestBuildWorkspaceContextMessage_EdgeCases(t *testing.T) {
	t.Run("empty conversation ID", func(t *testing.T) {
		result := buildWorkspaceContextMessage("", "user-123", []agentreq.SelectedFile{
			{FileName: "/workspace/test/file.csv"},
		})

		// Should not panic
		assert.NotEmpty(t, result)
	})

	t.Run("empty user ID", func(t *testing.T) {
		result := buildWorkspaceContextMessage("conv-123", "", []agentreq.SelectedFile{
			{FileName: "/workspace/conv-123/uploads/temparea/file.csv"},
		})

		// Should not panic
		assert.NotEmpty(t, result)
	})

	t.Run("file without matching path", func(t *testing.T) {
		result := buildWorkspaceContextMessage("conv-123", "user-456", []agentreq.SelectedFile{
			{FileName: "/some/other/path/file.csv"},
		})

		// Should not panic
		assert.NotEmpty(t, result)
	})
}
