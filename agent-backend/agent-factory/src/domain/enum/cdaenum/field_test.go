package cdaenum

import "testing"

func TestInputFieldType_EnumCheck(t *testing.T) {
	tests := []struct {
		name    string
		t       InputFieldType
		wantErr bool
	}{
		{
			name:    "字符串类型",
			t:       InputFieldTypeString,
			wantErr: false,
		},
		{
			name:    "文件类型",
			t:       InputFieldTypeFile,
			wantErr: false,
		},
		{
			name:    "JSON对象类型",
			t:       InputFieldTypeJSONObject,
			wantErr: false,
		},
		{
			name:    "无效类型",
			t:       InputFieldType("invalid"),
			wantErr: true,
		},
		{
			name:    "空字符串",
			t:       InputFieldType(""),
			wantErr: true,
		},
		{
			name:    "未知类型",
			t:       InputFieldType("text"),
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := tt.t.EnumCheck()
			if (err != nil) != tt.wantErr {
				t.Errorf("EnumCheck() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}
