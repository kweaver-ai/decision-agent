package helpers

import (
	"os"
	"testing"
)

func TestEnvConstants(t *testing.T) {
	t.Run("EnvPrefix constant", func(t *testing.T) {
		expected := "AGENT_FACTORY_"
		if EnvPrefix != expected {
			t.Errorf("Expected EnvPrefix to be '%s', got '%s'", expected, EnvPrefix)
		}
	})

	t.Run("EnvIsLocalDev constant", func(t *testing.T) {
		expected := "AGENT_FACTORY_LOCAL_DEV"
		if EnvIsLocalDev != expected {
			t.Errorf("Expected EnvIsLocalDev to be '%s', got '%s'", expected, EnvIsLocalDev)
		}
	})

	t.Run("constants are not empty", func(t *testing.T) {
		constants := []string{
			EnvPrefix,
			EnvIsLocalDev,
			isDebugMode,
			isSQLPrint,
			projPath,
			skipOauthVerify,
		}

		for _, constant := range constants {
			if constant == "" {
				t.Error("Expected constant to not be empty")
			}
		}
	})
}

func TestIsLocalDev(t *testing.T) {
	// Save original env value
	originalValue := os.Getenv(EnvIsLocalDev)

	// Clean up after test
	defer func() {
		if originalValue != "" {
			os.Setenv(EnvIsLocalDev, originalValue)
		} else {
			os.Unsetenv(EnvIsLocalDev)
		}
		// Reset mock
		mockIsLocalDev = false
	}()

	t.Run("env var true", func(t *testing.T) {
		os.Setenv(EnvIsLocalDev, "true")
		if !IsLocalDev() {
			t.Error("Expected IsLocalDev to return true")
		}
	})

	t.Run("env var false", func(t *testing.T) {
		os.Setenv(EnvIsLocalDev, "false")
		if IsLocalDev() {
			t.Error("Expected IsLocalDev to return false")
		}
	})

	t.Run("env var not set", func(t *testing.T) {
		os.Unsetenv(EnvIsLocalDev)
		if IsLocalDev() {
			t.Error("Expected IsLocalDev to return false when env not set")
		}
	})

	t.Run("mock is local dev", func(t *testing.T) {
		os.Unsetenv(EnvIsLocalDev)
		SetIsLocalDev()
		if !IsLocalDev() {
			t.Error("Expected IsLocalDev to return true when mock is set")
		}
	})
}

func TestIsAaronLocalDev(t *testing.T) {
	// Save original env value
	envVar := EnvIsLocalDev + "_AARON"
	originalValue := os.Getenv(envVar)

	// Clean up after test
	defer func() {
		if originalValue != "" {
			os.Setenv(envVar, originalValue)
		} else {
			os.Unsetenv(envVar)
		}
	}()

	t.Run("env var true", func(t *testing.T) {
		os.Setenv(envVar, "true")
		if !IsAaronLocalDev() {
			t.Error("Expected IsAaronLocalDev to return true")
		}
	})

	t.Run("env var false", func(t *testing.T) {
		os.Setenv(envVar, "false")
		if IsAaronLocalDev() {
			t.Error("Expected IsAaronLocalDev to return false")
		}
	})

	t.Run("env var not set", func(t *testing.T) {
		os.Unsetenv(envVar)
		if IsAaronLocalDev() {
			t.Error("Expected IsAaronLocalDev to return false when env not set")
		}
	})
}

func TestIsDebugMode(t *testing.T) {
	// Save original env value
	originalValue := os.Getenv(isDebugMode)

	// Clean up after test
	defer func() {
		if originalValue != "" {
			os.Setenv(isDebugMode, originalValue)
		} else {
			os.Unsetenv(isDebugMode)
		}
	}()

	t.Run("env var true", func(t *testing.T) {
		os.Setenv(isDebugMode, "true")
		if !IsDebugMode() {
			t.Error("Expected IsDebugMode to return true")
		}
	})

	t.Run("env var false", func(t *testing.T) {
		os.Setenv(isDebugMode, "false")
		if IsDebugMode() {
			t.Error("Expected IsDebugMode to return false")
		}
	})

	t.Run("env var not set", func(t *testing.T) {
		os.Unsetenv(isDebugMode)
		if IsDebugMode() {
			t.Error("Expected IsDebugMode to return false when env not set")
		}
	})
}

func TestIsOprLogShowLogForDebug(t *testing.T) {
	t.Run("test function exists", func(t *testing.T) {
		// This function calls IsDebugMode internally
		result := IsOprLogShowLogForDebug()
		// Result depends on environment
		_ = result
	})
}

func TestIsSQLPrint(t *testing.T) {
	// Save original env value
	originalValue := os.Getenv(isSQLPrint)

	// Clean up after test
	defer func() {
		if originalValue != "" {
			os.Setenv(isSQLPrint, originalValue)
		} else {
			os.Unsetenv(isSQLPrint)
		}
	}()

	t.Run("env var true", func(t *testing.T) {
		os.Setenv(isSQLPrint, "true")
		if !IsSQLPrint() {
			t.Error("Expected IsSQLPrint to return true")
		}
	})

	t.Run("env var false", func(t *testing.T) {
		os.Setenv(isSQLPrint, "false")
		if IsSQLPrint() {
			t.Error("Expected IsSQLPrint to return false")
		}
	})

	t.Run("env var not set", func(t *testing.T) {
		os.Unsetenv(isSQLPrint)
		if IsSQLPrint() {
			t.Error("Expected IsSQLPrint to return false when env not set")
		}
	})
}

func TestProjectPathByEnv(t *testing.T) {
	// Save original env value
	originalValue := os.Getenv(projPath)

	// Clean up after test
	defer func() {
		if originalValue != "" {
			os.Setenv(projPath, originalValue)
		} else {
			os.Unsetenv(projPath)
		}
	}()

	t.Run("env var set", func(t *testing.T) {
		expectedPath := "/custom/path"
		os.Setenv(projPath, expectedPath)

		result := ProjectPathByEnv()
		if result != expectedPath {
			t.Errorf("Expected '%s', got '%s'", expectedPath, result)
		}
	})

	t.Run("env var not set", func(t *testing.T) {
		os.Unsetenv(projPath)

		result := ProjectPathByEnv()
		if result != "" {
			t.Errorf("Expected empty string, got '%s'", result)
		}
	})
}

func TestIsSkipOauthVerify(t *testing.T) {
	// Save original env value
	originalValue := os.Getenv(skipOauthVerify)

	// Clean up after test
	defer func() {
		if originalValue != "" {
			os.Setenv(skipOauthVerify, originalValue)
		} else {
			os.Unsetenv(skipOauthVerify)
		}
	}()

	t.Run("env var true", func(t *testing.T) {
		os.Setenv(skipOauthVerify, "true")
		if !IsSkipOauthVerify() {
			t.Error("Expected IsSkipOauthVerify to return true")
		}
	})

	t.Run("env var false", func(t *testing.T) {
		os.Setenv(skipOauthVerify, "false")
		if IsSkipOauthVerify() {
			t.Error("Expected IsSkipOauthVerify to return false")
		}
	})

	t.Run("env var not set", func(t *testing.T) {
		os.Unsetenv(skipOauthVerify)
		if IsSkipOauthVerify() {
			t.Error("Expected IsSkipOauthVerify to return false when env not set")
		}
	})
}
