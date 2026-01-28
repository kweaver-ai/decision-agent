package daconfvalobj

import (
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/enum/cdaenum"
	"github.com/stretchr/testify/assert"
)

func TestInput_GetErrMsgMap(t *testing.T) {
	input := &Input{}
	msgMap := input.GetErrMsgMap()

	tests := []struct {
		name string
		key  string
		want string
	}{
		{
			name: "Fields.required",
			key:  "Fields.required",
			want: `"fields"不能为空`,
		},
		{
			name: "不存在的key",
			key:  "Unknown.key",
			want: "",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := msgMap[tt.key]
			if got != tt.want {
				t.Errorf("GetErrMsgMap()[%q] = %q, want %q", tt.key, got, tt.want)
			}
		})
	}
}

func TestInput_ValObjCheck(t *testing.T) {
	tests := []struct {
		name    string
		input   *Input
		wantErr bool
	}{
		{
			name: "有效配置",
			input: &Input{
				Fields: Fields{
					&Field{Name: "field1", Type: cdaenum.InputFieldTypeString},
				},
			},
			wantErr: false,
		},
		{
			name: "Fields为空",
			input: &Input{
				Fields: nil,
			},
			wantErr: true,
		},
		{
			name: "包含文件字段但缺少TempZoneConfig",
			input: &Input{
				Fields: Fields{
					&Field{Name: "file1", Type: cdaenum.InputFieldTypeFile},
				},
			},
			wantErr: true,
		},
		{
			name: "包含Rewrite且有效",
			input: &Input{
				Fields: Fields{
					&Field{Name: "field1", Type: cdaenum.InputFieldTypeString},
				},
				Rewrite: &Rewrite{
					Enable: func() *bool { b := false; return &b }(),
				},
			},
			wantErr: false,
		},
		{
			name: "包含Augment且有效",
			input: &Input{
				Fields: Fields{
					&Field{Name: "field1", Type: cdaenum.InputFieldTypeString},
				},
				Augment: &Augment{
					Enable: func() *bool { b := false; return &b }(),
					DataSource: &AugmentDataSource{
						Kg: []KgSource{},
					},
				},
			},
			wantErr: false,
		},
		{
			name: "所有配置有效",
			input: &Input{
				Fields: Fields{
					&Field{Name: "field1", Type: cdaenum.InputFieldTypeString},
				},
				Rewrite: &Rewrite{
					Enable: func() *bool { b := false; return &b }(),
				},
				Augment: &Augment{
					Enable: func() *bool { b := false; return &b }(),
					DataSource: &AugmentDataSource{
						Kg: []KgSource{},
					},
				}
			},
			wantErr: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := tt.input.ValObjCheck()
			if tt.wantErr {
				assert.Error(t, err, "expected error")
			} else {
				assert.NoError(t, err, "expected no error")
			}
		})
	}
}

func TestInput_SetIsTempZoneEnabled(t *testing.T) {
	tests := []struct {
		name               string
		input              *Input
		wantTempZoneStatus cdaenum.TempZoneStatus
	}{
		{
			name: "包含文件字段",
			input: &Input{
				Fields: Fields{
					&Field{Name: "file1", Type: cdaenum.InputFieldTypeFile},
				},
			},
			wantTempZoneStatus: cdaenum.TempZoneEnabled,
		},
		{
			name: "不包含文件字段",
			input: &Input{
				Fields: Fields{
					&Field{Name: "field1", Type: cdaenum.InputFieldTypeString},
				},
			},
			wantTempZoneStatus: cdaenum.TempZoneDisabled,
		},
		{
			name: "空字段列表",
			input: &Input{
				Fields: Fields{},
			},
			wantTempZoneStatus: cdaenum.TempZoneDisabled,
		},
		{
			name: "混合字段包含文件",
			input: &Input{
				Fields: Fields{
					&Field{Name: "field1", Type: cdaenum.InputFieldTypeString},
					&Field{Name: "file1", Type: cdaenum.InputFieldTypeFile},
				},
			},
			wantTempZoneStatus: cdaenum.TempZoneEnabled,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			tt.input.SetIsTempZoneEnabled()
			assert.Equal(t, tt.wantTempZoneStatus, tt.input.IsTempZoneEnabled, "IsTempZoneEnabled should match expected")
		})
	}
}
