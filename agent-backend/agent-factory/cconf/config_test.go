package cconf

import (
	"os"
	"testing"

	"github.com/kweaver-ai/kweaver-go-lib/rest"
)

func TestGetConfigPath(t *testing.T) {
	t.Run("default config path", func(t *testing.T) {
		// Reset the global variable
		_configPath = ""

		// Save original env value
		originalPath := os.Getenv("CONFIG_PATH")

		// Clean up after test
		defer func() {
			_configPath = ""
			if originalPath != "" {
				os.Setenv("CONFIG_PATH", originalPath)
			} else {
				os.Unsetenv("CONFIG_PATH")
			}
		}()

		path := GetConfigPath()

		// The path will be either /sysvol/conf or ./conf depending on what exists
		if path == "" {
			t.Error("Expected GetConfigPath to return a non-empty string")
		}
	})
}

func TestConfig_IsDebug(t *testing.T) {
	t.Run("debug mode true", func(t *testing.T) {
		config := &Config{
			Project: Project{
				Debug: true,
			},
		}

		if !config.IsDebug() {
			t.Error("Expected IsDebug to return true")
		}
	})

	t.Run("debug mode false", func(t *testing.T) {
		config := &Config{
			Project: Project{
				Debug: false,
			},
		}

		if config.IsDebug() {
			t.Error("Expected IsDebug to return false")
		}
	})
}

func TestConfig_GetDefaultLanguage(t *testing.T) {
	t.Run("simplified chinese", func(t *testing.T) {
		config := &Config{
			Project: Project{
				Language: rest.SimplifiedChinese,
			},
		}

		lang := config.GetDefaultLanguage()
		if lang != rest.SimplifiedChinese {
			t.Errorf("Expected SimplifiedChinese, got %v", lang)
		}
	})

	t.Run("american english", func(t *testing.T) {
		config := &Config{
			Project: Project{
				Language: rest.AmericanEnglish,
			},
		}

		lang := config.GetDefaultLanguage()
		if lang != rest.AmericanEnglish {
			t.Errorf("Expected AmericanEnglish, got %v", lang)
		}
	})
}

func TestConfig_GetLogLevelString(t *testing.T) {
	t.Run("log level 1", func(t *testing.T) {
		config := &Config{
			Project: Project{
				LoggerLevel: 1,
			},
		}

		level := config.GetLogLevelString()
		if level == "" {
			t.Error("Expected GetLogLevelString to return a non-empty string")
		}
	})
}

func TestConfig_String(t *testing.T) {
	t.Run("valid config", func(t *testing.T) {
		config := &Config{
			Project: Project{
				Host: "localhost",
				Port: 8080,
			},
		}

		str := config.String()
		if str == "" {
			t.Error("Expected String to return a non-empty string")
		}
	})
}

func TestBaseDefConfig(t *testing.T) {
	t.Run("default config values", func(t *testing.T) {
		config := BaseDefConfig()

		if config == nil {
			t.Fatal("Expected BaseDefConfig to return a non-nil config")
		}

		if config.Project.Host != "0.0.0.0" {
			t.Errorf("Expected Host to be '0.0.0.0', got '%s'", config.Project.Host)
		}
		if config.Project.Port != 30777 {
			t.Errorf("Expected Port to be 30777, got %d", config.Project.Port)
		}
		if config.Project.Language != rest.SimplifiedChinese {
			t.Errorf("Expected Language to be SimplifiedChinese, got %v", config.Project.Language)
		}
		if config.Project.Debug {
			t.Error("Expected Debug to be false")
		}
	})
}

func TestGetConfigBys(t *testing.T) {
	t.Run("test function exists", func(t *testing.T) {
		// This test verifies that GetConfigBys function exists
		// The actual functionality depends on file system
		// which is difficult to test in unit tests

		// Note: Calling this with a non-existent file will call log.Fatalf
		// which will terminate the test
		_ = GetConfigBys
	})
}

func TestLoadConfig(t *testing.T) {
	t.Run("test function exists", func(t *testing.T) {
		// This test verifies that LoadConfig function exists
		// The actual functionality depends on YAML unmarshaling
		// which is difficult to test in unit tests

		// Note: This will call log.Fatalf if the YAML is invalid
		_ = LoadConfig
	})
}

func TestConfig_Check(t *testing.T) {
	t.Run("valid project config", func(t *testing.T) {
		config := &Config{
			Project: Project{
				Host:     "localhost",
				Port:     8080,
				Language: rest.SimplifiedChinese,
			},
		}

		err := config.Check()
		if err != nil {
			t.Errorf("Expected Check to return no error, got %v", err)
		}
	})
}

func TestGetConfigPath_WithEnv(t *testing.T) {
	// Reset the global variable
	_configPath = ""

	// Save original env value
	originalPath := os.Getenv("AGENT_FACTORY_CONFIG_PATH")

	// Clean up after test
	defer func() {
		_configPath = ""
		if originalPath != "" {
			os.Setenv("AGENT_FACTORY_CONFIG_PATH", originalPath)
		} else {
			os.Unsetenv("AGENT_FACTORY_CONFIG_PATH")
		}
	}()

	// Set the environment variable
	os.Setenv("AGENT_FACTORY_CONFIG_PATH", "/custom/config/path")

	path := GetConfigPath()

	if path != "/custom/config/path" {
		t.Errorf("Expected '/custom/config/path', got '%s'", path)
	}
}

func TestGetConfigPath_Cached(t *testing.T) {
	// Set the global variable directly
	_configPath = "/cached/path"

	// Even if we set an env var, it should return the cached value
	os.Setenv("CONFIG_PATH", "/custom/path")
	defer os.Unsetenv("CONFIG_PATH")

	path := GetConfigPath()

	if path != "/cached/path" {
		t.Errorf("Expected '/cached/path', got '%s'", path)
	}
}
