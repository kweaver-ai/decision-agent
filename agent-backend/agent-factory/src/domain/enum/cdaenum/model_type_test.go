package cdaenum

import "testing"

func TestModelType_EnumCheck(t *testing.T) {
	tests := []struct {
		name    string
		t       ModelType
		wantErr bool
	}{
		{
			name:    "LLM类型",
			t:       ModelTypeLlm,
			wantErr: false,
		},
		{
			name:    "RLM类型",
			t:       ModelTypeRlm,
			wantErr: false,
		},
		{
			name:    "无效类型",
			t:       ModelType("invalid"),
			wantErr: true,
		},
		{
			name:    "空字符串",
			t:       ModelType(""),
			wantErr: true,
		},
		{
			name:    "未知类型",
			t:       ModelType("text"),
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
