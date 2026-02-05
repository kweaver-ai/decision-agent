package util

import "testing"

func TestGNS2ObjectID(t *testing.T) {
	tests := []struct {
		name string
		gns  string
		want string
	}{
		{"simple path", "/path/to/id123", "id123"},
		{"path with multiple segments", "a/b/c/d/object-id", "object-id"},
		{"single segment", "single", "single"},
		{"empty string", "", ""},
		{"no slashes", "objectId123", "objectId123"},
		{"trailing slash", "path/to/", ""},
		{"multiple slashes", "path///to/id", "id"},
		{"numeric id", "/api/v1/users/12345", "12345"},
		{"uuid format", "/api/v1/550e8400-e29b-41d4-a716-446655440000", "550e8400-e29b-41d4-a716-446655440000"},
		{"special characters", "/path/to/id-with_special.chars.123", "id-with_special.chars.123"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := GNS2ObjectID(tt.gns); got != tt.want {
				t.Errorf("GNS2ObjectID(%q) = %q, want %q", tt.gns, got, tt.want)
			}
		})
	}
}
