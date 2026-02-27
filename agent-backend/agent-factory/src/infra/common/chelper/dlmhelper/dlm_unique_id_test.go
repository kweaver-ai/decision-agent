package dlmhelper

import (
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestGenRedisDlmUniqueValue_GeneratesValue(t *testing.T) {
	t.Parallel()

	// Note: This test requires database access and will be skipped in most environments
	// as we don't want to create side effects during unit testing
	t.Skip("genRedisDlmUniqueValue requires database access, skipping to avoid side effects")
}

func TestDelRedisDlmUniqueValue_DeletesValue(t *testing.T) {
	t.Parallel()

	// Note: This test requires database access and will be skipped in most environments
	// as we don't want to create side effects during unit testing
	t.Skip("delRedisDlmUniqueValue requires database access, skipping to avoid side effects")
}

func TestGetDefaultDlmConf_DetailedOptions(t *testing.T) {
	t.Parallel()

	t.Run("verify options array structure", func(t *testing.T) {
		t.Parallel()

		redisKeyPrefix := "test:dlm:"
		conf := GetDefaultDlmConf(redisKeyPrefix)

		assert.NotNil(t, conf)
		assert.NotNil(t, conf.Options)
		assert.Greater(t, len(conf.Options), 0, "Options should not be empty")
	})

	t.Run("verify expiry configuration", func(t *testing.T) {
		t.Parallel()

		redisKeyPrefix := "test:dlm:"
		conf := GetDefaultDlmConf(redisKeyPrefix)

		// WatchDogInterval should be half of 20 seconds = 10 seconds
		expectedWatchDogInterval := 10 * 1000000000 // 10 seconds in nanoseconds
		assert.Equal(t, expectedWatchDogInterval, int(conf.WatchDogInterval))
	})

	t.Run("verify redis key prefix is set", func(t *testing.T) {
		t.Parallel()

		prefix := "myapp:lock:"
		conf := GetDefaultDlmConf(prefix)

		assert.Equal(t, prefix, conf.RedisKeyPrefix)
	})

	t.Run("verify delete value func is set", func(t *testing.T) {
		t.Parallel()

		conf := GetDefaultDlmConf("test:")

		assert.NotNil(t, conf.DeleteValueFunc, "DeleteValueFunc should not be nil")
	})

	t.Run("verify logger is set", func(t *testing.T) {
		t.Parallel()

		conf := GetDefaultDlmConf("test:")

		assert.NotNil(t, conf.Logger, "Logger should not be nil")
	})
}

func TestGetDefaultDlmConf_EdgeCases(t *testing.T) {
	t.Parallel()

	t.Run("empty redis key prefix", func(t *testing.T) {
		t.Parallel()

		conf := GetDefaultDlmConf("")

		assert.NotNil(t, conf)
		assert.Equal(t, "", conf.RedisKeyPrefix)
	})

	t.Run("redis key prefix with special characters", func(t *testing.T) {
		t.Parallel()

		specialPrefix := "test:dlm:with:special:chars:{}:"
		conf := GetDefaultDlmConf(specialPrefix)

		assert.Equal(t, specialPrefix, conf.RedisKeyPrefix)
	})

	t.Run("very long redis key prefix", func(t *testing.T) {
		t.Parallel()

		longPrefix := strings.Repeat("a:", 100)
		conf := GetDefaultDlmConf(longPrefix)

		assert.Equal(t, longPrefix, conf.RedisKeyPrefix)
	})
}

func TestGetDefaultDlmConf_Consistency(t *testing.T) {
	t.Parallel()

	t.Run("multiple calls return consistent config", func(t *testing.T) {
		t.Parallel()

		prefix := "test:consistency:"

		conf1 := GetDefaultDlmConf(prefix)
		conf2 := GetDefaultDlmConf(prefix)

		assert.Equal(t, conf1.RedisKeyPrefix, conf2.RedisKeyPrefix)
		assert.Equal(t, conf1.WatchDogInterval, conf2.WatchDogInterval)
	})
}
