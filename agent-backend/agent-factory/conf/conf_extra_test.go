package conf

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestSandboxPlatformConf_Struct(t *testing.T) {
	t.Run("create SandboxPlatformConf struct", func(t *testing.T) {
		sp := &SandboxPlatformConf{}

		assert.NotNil(t, sp)
	})
}

func TestDocsetConf_Struct(t *testing.T) {
	t.Run("create DocsetConf struct", func(t *testing.T) {
		dc := &DocsetConf{}

		assert.NotNil(t, dc)
	})
}

func TestUniqueryConf_Struct(t *testing.T) {
	t.Run("create UniqueryConf struct", func(t *testing.T) {
		uc := &UniqueryConf{}

		assert.NotNil(t, uc)
	})
}

func TestAgentExecutorConf_Struct(t *testing.T) {
	t.Run("create AgentExecutorConf struct", func(t *testing.T) {
		ae := &AgentExecutorConf{}

		assert.NotNil(t, ae)
	})
}

func TestConfig_Struct(t *testing.T) {
	t.Run("create Config struct", func(t *testing.T) {
		cfg := &Config{}

		assert.NotNil(t, cfg)
	})
}
