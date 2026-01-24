package cdaenum

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestDolphinMode_EnumCheck(t *testing.T) {
	tests := []struct {
		name    string
		d       DolphinMode
		wantErr bool
	}{
		{
			name:    "禁用模式",
			d:       DolphinModeDisabled,
			wantErr: false,
		},
		{
			name:    "启用模式",
			d:       DolphinModeEnabled,
			wantErr: false,
		},
		{
			name:    "负数",
			d:       DolphinMode(-1),
			wantErr: true,
		},
		{
			name:    "大于最大值",
			d:       DolphinMode(2),
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := tt.d.EnumCheck()
			if tt.wantErr {
				assert.Error(t, err, "expected error")
			} else {
				assert.NoError(t, err, "expected no error")
			}
		})
	}
}

func TestDolphinMode_Bool(t *testing.T) {
	tests := []struct {
		name string
		d    DolphinMode
		want bool
	}{
		{
			name: "禁用模式",
			d:    DolphinModeDisabled,
			want: false,
		},
		{
			name: "启用模式",
			d:    DolphinModeEnabled,
			want: true,
		},
		{
			name: "负数",
			d:    DolphinMode(-1),
			want: false,
		},
		{
			name: "大于最大值",
			d:    DolphinMode(2),
			want: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := tt.d.Bool()
			assert.Equal(t, tt.want, got, "Bool() should match expected")
		})
	}
}
