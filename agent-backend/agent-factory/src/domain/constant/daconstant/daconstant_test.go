package daconstant

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestAgentVersion_Constants(t *testing.T) {
	assert.Equal(t, "v0", AgentVersionUnpublished)
	assert.Equal(t, "latest", AgentVersionLatest)
}

func TestAgentInoutMaxSize(t *testing.T) {
	assert.Equal(t, 500, AgentInoutMaxSize)
}
