package daconfvalobj

import (
	"testing"
)

func TestTempZoneConfig_GetErrMsgMap(t *testing.T) {
	config := &TempZoneConfig{}
	msgMap := config.GetErrMsgMap()

	tests := []struct {
		name string
		key  string
		want string
	}{
		{
			name: "TmpFileUseType.required",
			key:  "TmpFileUseType.required",
			want: `"tmp_file_use_type"不能为空`,
		},
		{
			name: "SingleFileSizeLimit.required",
			key:  "SingleFileSizeLimit.required",
			want: `"single_file_size_limit"不能为空`,
		},
		{
			name: "SingleFileSizeLimitUnit.required",
			key:  "SingleFileSizeLimitUnit.required",
			want: `"single_file_size_limit_unit"不能为空`,
		},
		{
			name: "SupportDataType.required",
			key:  "SupportDataType.required",
			want: `"support_data_type"不能为空`,
		},
		{
			name: "AllowedFileCategories.required",
			key:  "AllowedFileCategories.required",
			want: `"allowed_file_categories"不能为空`,
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
