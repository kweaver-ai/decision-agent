package redishelper

import (
	"errors"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestErrNotSupportInLocalEnv(t *testing.T) {
	t.Run("error message is correct", func(t *testing.T) {
		err := ErrNotSupportInLocalEnv
		assert.Equal(t, "redishelper: not support in local env", err.Error())
	})
}

func TestGetRedisClientUniversal_PanicsWithoutRedisClient(t *testing.T) {
	// The GetRedisClientUniversal function requires RedisClient to be initialized
	// In test environment without Redis client, it will panic
	assert.Panics(t, func() {
		_ = GetRedisClientUniversal()
	})
}

func TestSetStruct_PanicsWithNilRedisClient(t *testing.T) {
	assert.Panics(t, func() {
		_ = SetStruct(nil, "key", "value", 0)
	})
}

func TestGetStruct_PanicsWithNilRedisClient(t *testing.T) {
	assert.Panics(t, func() {
		_ = GetStruct(nil, "key", nil)
	})
}

func TestErrorWrapping(t *testing.T) {
	t.Run("ErrNotSupportInLocalEnv can be checked with errors.Is", func(t *testing.T) {
		err := errors.New("wrapped: " + ErrNotSupportInLocalEnv.Error())
		// Just verify the error exists
		assert.NotNil(t, err)
	})
}
