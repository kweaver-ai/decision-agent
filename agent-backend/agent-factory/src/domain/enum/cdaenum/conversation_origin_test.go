package cdaenum

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestConversationOrigin_EnumCheck(t *testing.T) {
	tests := []struct {
		name    string
		t       ConversationOrigin
		wantErr bool
	}{
		{
			name:    "WebChat来源",
			t:       ConversationWebChat,
			wantErr: false,
		},
		{
			name:    "APICall来源",
			t:       ConversationAPICall,
			wantErr: false,
		},
		{
			name:    "无效来源",
			t:       ConversationOrigin("invalid"),
			wantErr: true,
		},
		{
			name:    "空字符串",
			t:       ConversationOrigin(""),
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := tt.t.EnumCheck()
			if tt.wantErr {
				assert.Error(t, err, "expected error")
			} else {
				assert.NoError(t, err, "expected no error")
			}
		})
	}
}
