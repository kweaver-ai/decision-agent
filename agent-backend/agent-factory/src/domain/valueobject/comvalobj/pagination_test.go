package comvalobj

import (
	"testing"
)

func TestPagination(t *testing.T) {
	tests := []struct {
		name string
		p    Pagination
	}{
		{
			name: "完整的分页信息",
			p: Pagination{
				Offset: 10,
				Limit:  20,
			},
		},
		{
			name: "零值",
			p: Pagination{
				Offset: 0,
				Limit:  0,
			},
		},
		{
			name: "大数值",
			p: Pagination{
				Offset: 1000,
				Limit:  500,
			},
		},
		{
			name: "负数",
			p: Pagination{
				Offset: -10,
				Limit:  -20,
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if tt.p.Offset != tt.p.Offset {
				t.Errorf("Offset = %d, want %d", tt.p.Offset, tt.p.Offset)
			}
			if tt.p.Limit != tt.p.Limit {
				t.Errorf("Limit = %d, want %d", tt.p.Limit, tt.p.Limit)
			}
		})
	}
}
