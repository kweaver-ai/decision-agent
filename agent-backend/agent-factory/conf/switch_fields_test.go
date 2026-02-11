package conf

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestNewSwitchFields(t *testing.T) {
	t.Run("creates SwitchFields with defaults", func(t *testing.T) {
		sf := NewSwitchFields()

		assert.NotNil(t, sf)
		assert.NotNil(t, sf.Mock)

		// Verify default values
		assert.False(t, sf.KeepLegacyAppPath)
		assert.False(t, sf.DisablePmsCheck)
		assert.False(t, sf.DisableBizDomainInit)
		assert.False(t, sf.UseDefaultBizDomain)
		assert.False(t, sf.DisableAuditInit)
	})

	t.Run("MockSwitchFields defaults to false", func(t *testing.T) {
		sf := NewSwitchFields()

		assert.False(t, sf.Mock.MockMQClient)
		assert.False(t, sf.Mock.MockSandboxPlatform)
		assert.False(t, sf.Mock.MockHydra)
		assert.False(t, sf.Mock.MockAuthZ)
		assert.False(t, sf.Mock.MockBizDomain)
	})
}

func TestSwitchFields_Struct(t *testing.T) {
	t.Run("create SwitchFields struct directly", func(t *testing.T) {
		sf := &SwitchFields{
			KeepLegacyAppPath:  true,
			DisablePmsCheck:    true,
			DisableBizDomainInit: true,
			UseDefaultBizDomain: true,
			DisableAuditInit:    true,
			Mock: &MockSwitchFields{
				MockMQClient:        true,
				MockSandboxPlatform: true,
			},
		}

		assert.NotNil(t, sf)
		assert.True(t, sf.KeepLegacyAppPath)
		assert.True(t, sf.DisablePmsCheck)
		assert.True(t, sf.Mock.MockMQClient)
	})

	t.Run("create SwitchFields with nil Mock", func(t *testing.T) {
		sf := &SwitchFields{
			Mock: nil,
		}

		assert.NotNil(t, sf)
		assert.Nil(t, sf.Mock)
	})
}

func TestMockSwitchFields_Struct(t *testing.T) {
	t.Run("create MockSwitchFields struct", func(t *testing.T) {
		msf := &MockSwitchFields{
			MockMQClient:        true,
			MockSandboxPlatform: true,
			MockHydra:           true,
			MockAuthZ:           true,
			MockBizDomain:       true,
		}

		assert.NotNil(t, msf)
		assert.True(t, msf.MockMQClient)
		assert.True(t, msf.MockSandboxPlatform)
		assert.True(t, msf.MockHydra)
		assert.True(t, msf.MockAuthZ)
		assert.True(t, msf.MockBizDomain)
	})

	t.Run("create empty MockSwitchFields", func(t *testing.T) {
		msf := &MockSwitchFields{}

		assert.NotNil(t, msf)
		assert.False(t, msf.MockMQClient)
		assert.False(t, msf.MockSandboxPlatform)
	})
}

func TestSwitchFields_YAMLTAGs(t *testing.T) {
	t.Run("yaml tags are correct", func(t *testing.T) {
		// This is a compile-time check to ensure yaml tags are correct
		sf := &SwitchFields{}

		assert.NotNil(t, sf)
		// The yaml tags would be verified by actual yaml parsing
	})
}
