package dainject

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"go.uber.org/mock/gomock"

	v3portdrivermock "github.com/kweaver-ai/decision-agent/agent-factory/src/port/driver/iv3portdriver/v3portdrivermock"
)

func TestNewObservabilitySvc_SingletonAndConstruct(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	initInjectGlobalConfig(t)
	resetInjectSingletons()

	// Pre-inject squareSvc mock to avoid real DB repo constructors panicking
	squareSvcOnce.Do(func() {
		squareSvcImpl = v3portdrivermock.NewMockISquareSvc(ctrl)
	})

	first := NewObservabilitySvc()
	second := NewObservabilitySvc()

	assert.NotNil(t, first)
	assert.Same(t, first, second)
}
