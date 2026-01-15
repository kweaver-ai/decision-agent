package cutil

import (
	"net/http"
	"testing"
)

func TestIsHttpErr(t *testing.T) {
	tests := []struct {
		name     string
		response *http.Response
		want     bool
	}{
		{
			name:     "status code less than 200 should be error",
			response: &http.Response{StatusCode: 199},
			want:     true,
		},
		{
			name:     "status code 300 and above should be error",
			response: &http.Response{StatusCode: 300},
			want:     true,
		},
		{
			name:     "status code 200 should not be error",
			response: &http.Response{StatusCode: 200},
			want:     false,
		},
		{
			name:     "status code 299 should not be error",
			response: &http.Response{StatusCode: 299},
			want:     false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := IsHttpErr(tt.response); got != tt.want {
				t.Errorf("IsHttpErr() = %v, want %v", got, tt.want)
			}
		})
	}
}
