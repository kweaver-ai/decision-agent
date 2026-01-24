package cdaenum

import "testing"

func TestBuiltIn_EnumCheck(t *testing.T) {
	tests := []struct {
		name    string
		b       BuiltIn
		wantErr bool
	}{
		{
			name:    "非内置",
			b:       BuiltInNo,
			wantErr: false,
		},
		{
			name:    "内置",
			b:       BuiltInYes,
			wantErr: false,
		},
		{
			name:    "无效值",
			b:       BuiltIn(2),
			wantErr: true,
		},
		{
			name:    "负数",
			b:       BuiltIn(-1),
			wantErr: true,
		},
		{
			name:    "大数值",
			b:       BuiltIn(100),
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := tt.b.EnumCheck()
			if (err != nil) != tt.wantErr {
				t.Errorf("EnumCheck() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}

func TestBuiltIn_IsBuiltIn(t *testing.T) {
	tests := []struct {
		name string
		b    *BuiltIn
		want bool
	}{
		{
			name: "nil指针",
			b:    nil,
			want: false,
		},
		{
			name: "内置",
			b:    func() *BuiltIn { v := BuiltInYes; return &v }(),
			want: true,
		},
		{
			name: "非内置",
			b:    func() *BuiltIn { v := BuiltInNo; return &v }(),
			want: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := tt.b.IsBuiltIn(); got != tt.want {
				t.Errorf("IsBuiltIn() = %v, want %v", got, tt.want)
			}
		})
	}
}
