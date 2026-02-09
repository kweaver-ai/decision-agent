package chatresenum

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestDocRetrievalStrategyStandard(t *testing.T) {
	assert.Equal(t, DocRetrievalStrategy("standard"), DocRetrievalStrategyStandard)
}

func TestDocRetrievalStrategy_NotEmpty(t *testing.T) {
	assert.NotEmpty(t, DocRetrievalStrategyStandard)
}

func TestDocRetrievalStrategy_String(t *testing.T) {
	strategy := DocRetrievalStrategyStandard
	assert.Equal(t, "standard", string(strategy))
}

func TestDocRetrievalStrategy_CustomValue(t *testing.T) {
	customStrategy := DocRetrievalStrategy("custom")
	assert.Equal(t, "custom", string(customStrategy))
}
