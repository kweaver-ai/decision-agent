package redishelper

import (
	"bytes"
	"net"
	"sync"
	"testing"
	"time"

	redis "github.com/go-redis/redis/v8"
	"github.com/kweaver-ai/decision-agent/agent-factory/cconf"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func startFakeRedisServer(t *testing.T) (host string, port string, shutdown func()) {
	t.Helper()

	ln, err := net.Listen("tcp", "127.0.0.1:0")
	require.NoError(t, err)

	done := make(chan struct{})

	var wg sync.WaitGroup

	writeResp := func(conn net.Conn, payload []byte) {
		resp := []byte("+OK\r\n")
		if bytes.Contains(bytes.ToUpper(payload), []byte("PING")) {
			resp = []byte("+PONG\r\n")
		}

		_, _ = conn.Write(resp)
	}

	wg.Add(1)

	go func() {
		defer wg.Done()

		for {
			conn, acceptErr := ln.Accept()
			if acceptErr != nil {
				select {
				case <-done:
					return
				default:
					return
				}
			}

			wg.Add(1)

			go func(c net.Conn) {
				defer wg.Done()
				defer c.Close()

				buf := make([]byte, 4096)

				for {
					_ = c.SetReadDeadline(time.Now().Add(100 * time.Millisecond))

					n, readErr := c.Read(buf)
					if n > 0 {
						writeResp(c, buf[:n])
					}

					if readErr != nil {
						if netErr, ok := readErr.(net.Error); ok && netErr.Timeout() {
							select {
							case <-done:
								return
							default:
								continue
							}
						}

						return
					}
				}
			}(conn)
		}
	}()

	host, port, err = net.SplitHostPort(ln.Addr().String())
	require.NoError(t, err)

	shutdown = func() {
		close(done)

		_ = ln.Close()

		wg.Wait()
	}

	return host, port, shutdown
}

func TestRedisConstants(t *testing.T) {
	t.Parallel()

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
			t.Parallel()
			assert.Equal(t, tt.expected, tt.constant)
		})
	}
}

func TestRedisConstants_AllUnique(t *testing.T) {
	t.Parallel()

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
	t.Parallel()

	assert.NotEmpty(t, MasterSlaveType, "MasterSlaveType should not be empty")
	assert.NotEmpty(t, StandaloneType, "StandaloneType should not be empty")
	assert.NotEmpty(t, SentinelType, "SentinelType should not be empty")
	assert.NotEmpty(t, ClusterType, "ClusterType should not be empty")
}

func TestStandalone_DefaultsAndOptions(t *testing.T) {
	t.Parallel()

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

func TestMasterSlave_DefaultsAndOptions(t *testing.T) {
	t.Parallel()

	conf := &cconf.RedisConf{}

	client := masterSlave(conf)

	t.Cleanup(func() {
		_ = client.Close()
	})

	redisClient, ok := client.(*redis.Client)
	require.True(t, ok)
	require.NotNil(t, redisClient)

	assert.Equal(t, "proton-redis-proton-redis.resource.svc.cluster.local", conf.MasterHost)
	assert.Equal(t, "6379", conf.MasterPort)
	assert.Equal(t, conf.MasterHost+":"+conf.MasterPort, redisClient.Options().Addr)
}

func TestSentinel_Defaults(t *testing.T) {
	t.Parallel()

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
	t.Parallel()

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
	t.Parallel()

	originalClient := redisClient

	t.Cleanup(func() {
		redisClient = originalClient
	})

	t.Run("panic when not connected", func(t *testing.T) {
		t.Parallel()

		redisClient = nil

		assert.Panics(t, func() {
			_ = RedisClient()
		})
	})

	t.Run("return client when connected", func(t *testing.T) {
		t.Parallel()

		connectedClient := redis.NewClient(&redis.Options{Addr: "127.0.0.1:6379"})

		t.Cleanup(func() {
			_ = connectedClient.Close()
		})

		redisClient = connectedClient

		assert.Equal(t, connectedClient, RedisClient())
	})
}

func TestConnectRedis_UnsupportedType_ReturnsNil(t *testing.T) {
	// t.Parallel() - 移除：此测试调用 ConnectRedis 单例函数，在并发环境下会导致 sync.Once 死锁
	originalOnce := redisOnce //nolint:govet
	originalClient := redisClient

	t.Cleanup(func() {
		redisOnce = originalOnce //nolint:govet
		redisClient = originalClient
	})

	redisOnce = sync.Once{}
	redisClient = nil

	client := ConnectRedis(&cconf.RedisConf{ConnectType: "unsupported"})
	assert.Nil(t, client)
}

func TestConnectRedis_StandaloneType_Success(t *testing.T) {
	// t.Parallel() - 移除：此测试调用 ConnectRedis 单例函数，在并发环境下会导致 sync.Once 死锁
	host, port, shutdown := startFakeRedisServer(t)
	t.Cleanup(shutdown)

	originalOnce := redisOnce //nolint:govet
	originalClient := redisClient

	t.Cleanup(func() {
		redisOnce = originalOnce //nolint:govet
		redisClient = originalClient
	})

	redisOnce = sync.Once{}
	redisClient = nil

	client := ConnectRedis(&cconf.RedisConf{ConnectType: StandaloneType, Host: host, Port: port})
	require.NotNil(t, client)
	t.Cleanup(func() {
		_ = client.Close()
	})

	assert.IsType(t, &redis.Client{}, client)
	assert.Equal(t, client, redisClient)
}

func TestConnectRedis_MasterSlaveType_Success(t *testing.T) {
	// t.Parallel() - 移除：此测试调用 ConnectRedis 单例函数，在并发环境下会导致 sync.Once 死锁
	host, port, shutdown := startFakeRedisServer(t)
	t.Cleanup(shutdown)

	originalOnce := redisOnce //nolint:govet
	originalClient := redisClient

	t.Cleanup(func() {
		redisOnce = originalOnce //nolint:govet
		redisClient = originalClient
	})

	redisOnce = sync.Once{}
	redisClient = nil

	client := ConnectRedis(&cconf.RedisConf{ConnectType: MasterSlaveType, MasterHost: host, MasterPort: port})
	require.NotNil(t, client)
	t.Cleanup(func() {
		_ = client.Close()
	})

	assert.IsType(t, &redis.Client{}, client)
	assert.Equal(t, client, redisClient)
}
