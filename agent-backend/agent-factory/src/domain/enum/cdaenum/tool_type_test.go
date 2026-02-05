package cdaenum

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestToolType_EnumCheck(t *testing.T) {
	tests := []struct {
		name    string
		t       ToolType
		wantErr bool
	}{
		{
			name:    "Tool类型",
			t:       ToolTypeTool,
			wantErr: false,
		},
		{
			name:    "Agent类型",
			t:       ToolTypeAgent,
			wantErr: false,
		},
		{
			name:    "无效类型",
			t:       ToolType("invalid"),
			wantErr: true,
		},
		{
			name:    "空字符串",
			t:       ToolType(""),
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
