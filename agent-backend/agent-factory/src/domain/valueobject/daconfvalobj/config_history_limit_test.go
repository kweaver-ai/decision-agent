package daconfvalobj

import (
	"context"
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/enum/cdaenum"
	"github.com/stretchr/testify/assert"
)

func TestConfig_HistoryLimitValidation(t *testing.T) {
	t.Parallel()

	tests := []struct {
		name    string
		input   int
		want    int
		wantErr bool
		errMsg  string
	}{
		{
			name:    "0 should convert to default 4",
			input:   0,
			want:    4,
			wantErr: false,
		},
		{
			name:    "4 is valid",
			input:   4,
			want:    4,
			wantErr: false,
		},
		{
			name:    "20 is max valid",
			input:   20,
			want:    20,
			wantErr: false,
		},
		{
			name:    "10 is valid",
			input:   10,
			want:    10,
			wantErr: false,
		},
		{
			name:    "-1 is invalid",
			input:   -1,
			want:    0,
			wantErr: true,
			errMsg:  "must be between",
		},
		{
			name:    "21 is invalid",
			input:   21,
			want:    0,
			wantErr: true,
			errMsg:  "must be between",
		},
		{
			name:    "100 is invalid",
			input:   100,
			want:    0,
			wantErr: true,
			errMsg:  "must be between",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			t.Parallel()

			config := &Config{
				Input:  &Input{},
				Output: &Output{},
			}
			config.Input.Fields = Fields{}
			config.Output.Variables = &VariablesS{}
			config.Output.DefaultFormat = cdaenum.OutputDefaultFormatJson

			config.HistoryLimit = tt.input

			err := config.ValObjCheckWithCtx(context.Background(), true)

			if tt.wantErr {
				assert.Error(t, err)
				assert.Contains(t, err.Error(), tt.errMsg)
			} else {
				assert.NoError(t, err)
				assert.Equal(t, tt.want, config.HistoryLimit)
			}
		})
	}
}

func TestConfig_HistoryLimitConstants(t *testing.T) {
	t.Parallel()

	assert.Equal(t, 4, DefaultHistoryLimit)
	assert.Equal(t, 20, MaxHistoryLimit)
}
