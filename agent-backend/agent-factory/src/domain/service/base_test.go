package service

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestNewSvcBase(t *testing.T) {
	svcBase := NewSvcBase()

	assert.NotNil(t, svcBase)
	assert.NotNil(t, svcBase.Logger)
}

func TestNewSvcBase_CreatesNewInstance(t *testing.T) {
	svcBase1 := NewSvcBase()
	svcBase2 := NewSvcBase()

	assert.NotNil(t, svcBase1)
	assert.NotNil(t, svcBase2)
	// Logger is a singleton, so both instances will have the same logger
	assert.Equal(t, svcBase1.Logger, svcBase2.Logger)
	// But the service base instances themselves are different
	assert.NotSame(t, svcBase1, svcBase2)
}

func TestSvcBase_StructFields(t *testing.T) {
	svcBase := &SvcBase{}

	assert.NotNil(t, svcBase)
	// Logger is nil when using struct literal
	assert.Nil(t, svcBase.Logger)
}
