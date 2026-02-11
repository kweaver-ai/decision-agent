package config

import (
	"testing"
	"github.com/stretchr/testify/assert"
)

func TestConfig_Register_LocaleSupport(t *testing.T) {
	// Test that locale package registers its supported locales
	// This is a simple initialization test
	assert.NotPanics(t, func() {
		_ = Register()
	})
}

func TestConfig_GetOtelDefaults(t *testing.T) {
	// Test getting OTel defaults
	// Since config is typically a singleton, we just verify the function can be called
	assert.NotPanics(t, func() {
		_ = GetOtelDefaults()
	})
}

func TestConfig_GetBaseDefConfig(t *testing.T) {
	// Test getting base definition config
	assert.NotPanics(t, func() {
		_ = GetBaseDefConfig()
	})
}
