package comvalobj

import (
	"testing"
)

func TestPagination(t *testing.T) {
	tests := []struct {
		name   string
		offset int
		limit  int
	}{
		{
			name:   "零值",
			offset: 0,
			limit:   0,
		},
		{
			name:   "正数",
			offset: 10,
			limit:  20,
		},
		{
			name:   "大数",
			offset: 1000,
			limit: 5000,
		},
		{
			name:   "负数",
			offset: -10,
			limit: -20,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			p := &Pagination{
				Offset: tt.offset,
				Limit:  tt.limit,
			}
			if p.Offset != tt.offset {
				t.Errorf("Offset = %d, want %d", p.Offset, tt.offset)
			}
			if p.Limit != tt.limit {
				t.Errorf("Limit = %d, want %d", p.Limit, tt.limit)
			}
		})
	}
}
