package personalspaceresp

import (
	"encoding/base64"
	"encoding/json"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestNewPAListPaginationMarker(t *testing.T) {
	marker := NewPAListPaginationMarker()

	assert.NotNil(t, marker)
	assert.IsType(t, &PAListPaginationMarker{}, marker)
}

func TestPAListPaginationMarker_ToString(t *testing.T) {
	tests := []struct {
		name    string
		marker  *PAListPaginationMarker
		wantErr bool
	}{
		{
			name:    "valid marker",
			marker:  &PAListPaginationMarker{UpdatedAt: 12345, LastAgentID: "agent-123"},
			wantErr: false,
		},
		{
			name:    "empty marker",
			marker:  &PAListPaginationMarker{},
			wantErr: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			str, err := tt.marker.ToString()

			if tt.wantErr {
				assert.Error(t, err)
				assert.Empty(t, str)
			} else {
				assert.NoError(t, err)
				assert.NotEmpty(t, str)

				// Verify it's valid base64
				_, err = base64.StdEncoding.DecodeString(str)
				assert.NoError(t, err)
			}
		})
	}
}

func TestPAListPaginationMarker_LoadFromStr(t *testing.T) {
	tests := []struct {
		name    string
		str     string
		wantErr bool
		check   func(t *testing.T, m *PAListPaginationMarker)
	}{
		{
			name:    "empty string",
			str:     "",
			wantErr: false,
			check: func(t *testing.T, m *PAListPaginationMarker) {
				assert.Equal(t, int64(0), m.UpdatedAt)
				assert.Empty(t, m.LastAgentID)
			},
		},
		{
			name:    "invalid base64",
			str:     "invalid base64!",
			wantErr: true,
			check:   nil,
		},
		{
			name:    "invalid json after base64",
			str:     base64.StdEncoding.EncodeToString([]byte("invalid json")),
			wantErr: true,
			check:   nil,
		},
		{
			name: "valid marker string",
			str: func() string {
				m := &PAListPaginationMarker{UpdatedAt: 12345, LastAgentID: "agent-123"}
				jsonStr, _ := json.Marshal(m)
				return base64.StdEncoding.EncodeToString(jsonStr)
			}(),
			wantErr: false,
			check: func(t *testing.T, m *PAListPaginationMarker) {
				assert.Equal(t, int64(12345), m.UpdatedAt)
				assert.Equal(t, "agent-123", m.LastAgentID)
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			marker := &PAListPaginationMarker{}
			err := marker.LoadFromStr(tt.str)

			if tt.wantErr {
				assert.Error(t, err)
			} else {
				require.NoError(t, err)
				if tt.check != nil {
					tt.check(t, marker)
				}
			}
		})
	}
}

func TestPAListPaginationMarker_RoundTrip(t *testing.T) {
	original := &PAListPaginationMarker{
		UpdatedAt:   987654321,
		LastAgentID: "agent-xyz",
	}

	// Convert to string and back
	str, err := original.ToString()
	require.NoError(t, err)

	restored := &PAListPaginationMarker{}
	err = restored.LoadFromStr(str)
	require.NoError(t, err)

	assert.Equal(t, original.UpdatedAt, restored.UpdatedAt)
	assert.Equal(t, original.LastAgentID, restored.LastAgentID)
}

func TestPAListPaginationMarker_RoundTripWithEmpty(t *testing.T) {
	original := &PAListPaginationMarker{}

	// Convert to string and back
	str, err := original.ToString()
	require.NoError(t, err)

	restored := &PAListPaginationMarker{}
	err = restored.LoadFromStr(str)
	require.NoError(t, err)

	assert.Equal(t, int64(0), restored.UpdatedAt)
	assert.Empty(t, restored.LastAgentID)
}

func TestPAListPaginationMarker_LoadFromStr_InvalidBase64InMiddle(t *testing.T) {
	// Create a valid JSON but with invalid base64 padding
	marker := &PAListPaginationMarker{}

	// Valid JSON but string is not properly encoded
	invalidStr := "eyJVXBkYXRlZEF0IjoxMjM0NSwiTGFzdEFnZW50SUQiOiJhZ2VudC0xMjMifQ==invalid"

	err := marker.LoadFromStr(invalidStr)
	assert.Error(t, err)
}

func TestPAListPaginationMarker_LoadFromStr_InvalidJSON(t *testing.T) {
	// Valid base64 but invalid JSON
	invalidJSON := base64.StdEncoding.EncodeToString([]byte("{invalid json}"))

	marker := &PAListPaginationMarker{}
	err := marker.LoadFromStr(invalidJSON)

	assert.Error(t, err)
}

func TestPAListPaginationMarker_Fields(t *testing.T) {
	marker := &PAListPaginationMarker{
		UpdatedAt:   1640995200000,
		LastAgentID: "test-agent-123",
	}

	assert.Equal(t, int64(1640995200000), marker.UpdatedAt)
	assert.Equal(t, "test-agent-123", marker.LastAgentID)
}
