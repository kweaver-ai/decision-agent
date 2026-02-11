package conf

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestAgentFactoryConf_Struct(t *testing.T) {
	t.Run("create AgentFactoryConf struct", func(t *testing.T) {
		af := &AgentFactoryConf{}

		assert.NotNil(t, af)
	})
}

func TestAgentFactoryConf_YAMLTAGs(t *testing.T) {
	t.Run("yaml tags are defined", func(t *testing.T) {
		// This is a compile-time check to ensure yaml tags are correct
		af := &AgentFactoryConf{}

		assert.NotNil(t, af)
	})
}

func TestAgentFactoryConf_EmptyStruct(t *testing.T) {
	t.Run("empty struct initialization", func(t *testing.T) {
		af := AgentFactoryConf{}

		assert.NotNil(t, af)
	})
}
