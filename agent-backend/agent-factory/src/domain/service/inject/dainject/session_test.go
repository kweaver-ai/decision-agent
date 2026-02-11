package dainject

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestNewSessionSvc_ReturnsService(t *testing.T) {
	// The NewSessionSvc function initializes with mock dependencies in test mode
	svc := NewSessionSvc()
	assert.NotNil(t, svc)
}


