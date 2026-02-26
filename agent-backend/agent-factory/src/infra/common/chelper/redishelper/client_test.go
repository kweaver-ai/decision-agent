package redishelper

import (
	"testing"

	redis "github.com/go-redis/redis/v8"
	"github.com/kweaver-ai/decision-agent/agent-factory/cconf"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
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

func TestStandalone_DefaultsAndOptions(t *testing.T) {
	conf := &cconf.RedisConf{}

	client := standalone(conf)
	t.Cleanup(func() {
		_ = client.Close()
	})

	redisClient, ok := client.(*redis.Client)
	require.True(t, ok)
	require.NotNil(t, redisClient)

	assert.Equal(t, "proton-redis-proton-redis.resource.svc.cluster.local", conf.Host)
	assert.Equal(t, "6379", conf.Port)
	assert.Equal(t, conf.Host+":"+conf.Port, redisClient.Options().Addr)
}

func TestSentinel_Defaults(t *testing.T) {
	conf := &cconf.RedisConf{}

	client := sentinel(conf)
	t.Cleanup(func() {
		_ = client.Close()
	})

	redisClient, ok := client.(*redis.Client)
	require.True(t, ok)
	require.NotNil(t, redisClient)

	assert.Equal(t, "mymaster", conf.MasterGroupName)
	assert.Equal(t, "eisoo.com123", conf.SentinelPwd)
	assert.Equal(t, "proton-redis-proton-redis-sentinel.resource.svc.cluster.local", conf.SentinelHost)
	assert.Equal(t, "26379", conf.SentinelPort)
}

func TestCluster_DefaultsAndOptions(t *testing.T) {
	conf := &cconf.RedisConf{
		ClusterHosts: []string{"127.0.0.1:7001", "127.0.0.1:7002"},
	}

	client := cluster(conf)
	t.Cleanup(func() {
		_ = client.Close()
	})

	clusterClient, ok := client.(*redis.ClusterClient)
	require.True(t, ok)
	require.NotNil(t, clusterClient)

	assert.Equal(t, "eisoo.com123", conf.ClusterPwd)
	assert.Equal(t, conf.ClusterHosts, clusterClient.Options().Addrs)
	assert.Equal(t, conf.ClusterPwd, clusterClient.Options().Password)
}

func TestRedisClient(t *testing.T) {
	originalClient := redisClient
	t.Cleanup(func() {
		redisClient = originalClient
	})

	t.Run("panic when not connected", func(t *testing.T) {
		redisClient = nil

		assert.Panics(t, func() {
			_ = RedisClient()
		})
	})

	t.Run("return client when connected", func(t *testing.T) {
		connectedClient := redis.NewClient(&redis.Options{Addr: "127.0.0.1:6379"})
		t.Cleanup(func() {
			_ = connectedClient.Close()
		})
		redisClient = connectedClient

		assert.Equal(t, connectedClient, RedisClient())
	})
}
