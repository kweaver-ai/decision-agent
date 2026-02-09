package cdaconstant

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestAgentVersionUnpublished(t *testing.T) {
	assert.Equal(t, "v0", AgentVersionUnpublished)
}

func TestAgentVersionLatest(t *testing.T) {
	assert.Equal(t, "latest", AgentVersionLatest)
}

func TestAgentVersionConstants_NotEmpty(t *testing.T) {
	assert.NotEmpty(t, AgentVersionUnpublished)
	assert.NotEmpty(t, AgentVersionLatest)
}

func TestAgentVersionConstants_AreUnique(t *testing.T) {
	assert.NotEqual(t, AgentVersionUnpublished, AgentVersionLatest)
}
