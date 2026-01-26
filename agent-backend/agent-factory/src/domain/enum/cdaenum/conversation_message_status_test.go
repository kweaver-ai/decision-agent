package cdaenum

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestConversationMsgStatus_EnumCheck(t *testing.T) {
	tests := []struct {
		name    string
		t       ConversationMsgStatus
		wantErr bool
	}{
		{
			name:    "Received状态",
			t:       MsgStatusReceived,
			wantErr: false,
		},
		{
			name:    "Processed状态",
			t:       MsgStatusProcessed,
			wantErr: false,
		},
		{
			name:    "Processing状态",
			t:       MsgStatusProcessing,
			wantErr: false,
		},
		{
			name:    "Succeded状态",
			t:       MsgStatusSucceded,
			wantErr: false,
		},
		{
			name:    "Failed状态",
			t:       MsgStatusFailed,
			wantErr: false,
		},
		{
			name:    "Cancelled状态",
			t:       MsgStatusCancelled,
			wantErr: false,
		},
		{
			name:    "无效状态",
			t:       ConversationMsgStatus("invalid"),
			wantErr: true,
		},
		{
			name:    "空字符串",
			t:       ConversationMsgStatus(""),
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
