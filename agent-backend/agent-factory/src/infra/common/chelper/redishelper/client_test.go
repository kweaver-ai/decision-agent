package redishelper

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestRedisConstants(t *testing.T) {
	tests := []struct {
		name     string
		constant string
		expected string
	}{
		{
			name:     "MasterSlaveType constant",
			constant: MasterSlaveType,
			expected: "master-slave",
		},
		{
			name:     "StandaloneType constant",
			constant: StandaloneType,
			expected: "standalone",
		},
		{
			name:     "SentinelType constant",
			constant: SentinelType,
			expected: "sentinel",
		},
		{
			name:     "ClusterType constant",
			constant: ClusterType,
			expected: "cluster",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			assert.Equal(t, tt.expected, tt.constant)
		})
	}
}

func TestRedisClient_NotConnected(t *testing.T) {
	// Note: This test is designed to verify the panic behavior when redis client is not connected
	// In a real test environment, the redis client might already be initialized
	// So we just verify that RedisClient() returns a non-nil value if initialized
	// or panics if not initialized

	// Since we can't control the redis client initialization state in a unit test
	// without causing side effects, we'll skip this test
	t.Skip("RedisClient() requires redis initialization, skipping to avoid side effects")
}

func TestRedisConstants_AllUnique(t *testing.T) {
	// Verify that all Redis type constants are unique
	constants := map[string]string{
		"MasterSlaveType": MasterSlaveType,
		"StandaloneType":  StandaloneType,
		"SentinelType":    SentinelType,
		"ClusterType":     ClusterType,
	}

	seen := make(map[string]bool)
	for name, value := range constants {
		if seen[value] {
			t.Errorf("Duplicate value found: %s (%s)", value, name)
		}
		seen[value] = true
	}

	// Verify we have 4 unique values
	assert.Len(t, seen, 4, "Should have 4 unique Redis type constants")
}

func TestRedisConstants_NonEmpty(t *testing.T) {
	assert.NotEmpty(t, MasterSlaveType, "MasterSlaveType should not be empty")
	assert.NotEmpty(t, StandaloneType, "StandaloneType should not be empty")
	assert.NotEmpty(t, SentinelType, "SentinelType should not be empty")
	assert.NotEmpty(t, ClusterType, "ClusterType should not be empty")
}
