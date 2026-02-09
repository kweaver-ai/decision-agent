package pubedeo

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestAgentPublishedInfoEo_NewAgentPublishedInfoEo(t *testing.T) {
	info := &AgentPublishedInfoEo{}

	assert.NotNil(t, info)
}

func TestAgentPublishedInfoEo_Empty(t *testing.T) {
	info := &AgentPublishedInfoEo{}

	assert.NotNil(t, info.PublishedToBeStruct)
}
