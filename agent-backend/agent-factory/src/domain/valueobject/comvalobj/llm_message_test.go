package comvalobj

import (
	"testing"
)

func TestLLMMessage(t *testing.T) {
	tests := []struct {
		name    string
		message *LLMMessage
	}{
		{
			name: "User消息",
			message: &LLMMessage{
				Role:    "user",
				Content: "test content",
			},
		},
		{
			name: "Assistant消息",
			message: &LLMMessage{
				Role:    "assistant",
				Content: "test response",
			},
		},
		{
			name: "System消息",
			message: &LLMMessage{
				Role:    "system",
				Content: "system prompt",
			},
		},
		{
			name: "空消息",
			message: &LLMMessage{
				Role:    "",
				Content: "",
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if tt.message.Role != tt.message.Role {
				t.Errorf("Role = %s, want %s", tt.message.Role, tt.message.Role)
			}
			if tt.message.Content != tt.message.Content {
				t.Errorf("Content = %s, want %s", tt.message.Content, tt.message.Content)
			}
		})
	}
}
