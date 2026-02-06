package daenum

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestPublishToWhere_EnumCheck(t *testing.T) {
	tests := []struct {
		name    string
		ptw     PublishToWhere
		wantErr bool
	}{
		{
			name:    "valid custom space",
			ptw:     PublishToWhereCustomSpace,
			wantErr: false,
		},
		{
			name:    "valid square",
			ptw:     PublishToWhereSquare,
			wantErr: false,
		},
		{
			name:    "invalid type",
			ptw:     PublishToWhere("invalid"),
			wantErr: true,
		},
		{
			name:    "empty type",
			ptw:     PublishToWhere(""),
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := tt.ptw.EnumCheck()
			if tt.wantErr {
				assert.Error(t, err)
			} else {
				assert.NoError(t, err)
			}
		})
	}
}
