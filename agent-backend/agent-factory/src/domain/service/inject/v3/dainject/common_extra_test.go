package dainject

import (
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/cconf"
	"github.com/stretchr/testify/assert"
)

// TestGetModelApiUrlPrefix_ValidConfig tests getModelApiUrlPrefix with valid configuration
func TestGetModelApiUrlPrefix_ValidConfig(t *testing.T) {
	conf := &cconf.ModelFactoryConf{
		ModelApiSvc: cconf.SvcConf{
			Protocol: "https",
			Host:     "example.com",
			Port:     8080,
		},
	}

	result := getModelApiUrlPrefix(conf)
	assert.NotEmpty(t, result)
	assert.Contains(t, result, "https://")
	assert.Contains(t, result, "example.com")
	assert.Contains(t, result, "8080")
	assert.Contains(t, result, "/api/private/mf-model-api/v1")
}

// TestGetModelApiUrlPrefix_HTTPProtocol tests getModelApiUrlPrefix with HTTP protocol
func TestGetModelApiUrlPrefix_HTTPProtocol(t *testing.T) {
	conf := &cconf.ModelFactoryConf{
		ModelApiSvc: cconf.SvcConf{
			Protocol: "http",
			Host:     "localhost",
			Port:     3000,
		},
	}

	result := getModelApiUrlPrefix(conf)
	assert.NotEmpty(t, result)
	assert.Contains(t, result, "http://localhost:3000/api/private/mf-model-api/v1")
}

// TestGetModelApiUrlPrefix_HostWithPortParsing tests getModelApiUrlPrefix with host containing port
func TestGetModelApiUrlPrefix_HostWithPortParsing(t *testing.T) {
	conf := &cconf.ModelFactoryConf{
		ModelApiSvc: cconf.SvcConf{
			Protocol: "https",
			Host:     "example.com:9000",
			Port:     8080,
		},
	}

	result := getModelApiUrlPrefix(conf)
	assert.NotEmpty(t, result)
	// The function uses ParseHost which extracts the host without port
	assert.Contains(t, result, "https://example.com:8080")
}

// TestGetModelApiUrlPrefix_DifferentPorts tests getModelApiUrlPrefix with various port numbers
func TestGetModelApiUrlPrefix_DifferentPorts(t *testing.T) {
	tests := []struct {
		name     string
		port     int
		expected string
	}{
		{"port 80", 80, "80"},
		{"port 443", 443, "443"},
		{"port 8080", 8080, "8080"},
		{"port 9000", 9000, "9000"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			conf := &cconf.ModelFactoryConf{
				ModelApiSvc: cconf.SvcConf{
					Protocol: "http",
					Host:     "example.com",
					Port:     tt.port,
				},
			}

			result := getModelApiUrlPrefix(conf)
			assert.Contains(t, result, tt.expected)
		})
	}
}

// TestGetModelApiUrlPrefix_IPAddress tests getModelApiUrlPrefix with IP address
func TestGetModelApiUrlPrefix_IPAddress(t *testing.T) {
	conf := &cconf.ModelFactoryConf{
		ModelApiSvc: cconf.SvcConf{
			Protocol: "http",
			Host:     "192.168.1.1",
			Port:     8000,
		},
	}

	result := getModelApiUrlPrefix(conf)
	assert.NotEmpty(t, result)
	assert.Contains(t, result, "http://192.168.1.1:8000/api/private/mf-model-api/v1")
}

// TestGetModelApiUrlPrefix_Localhost tests getModelApiUrlPrefix with localhost
func TestGetModelApiUrlPrefix_Localhost(t *testing.T) {
	conf := &cconf.ModelFactoryConf{
		ModelApiSvc: cconf.SvcConf{
			Protocol: "http",
			Host:     "localhost",
			Port:     5000,
		},
	}

	result := getModelApiUrlPrefix(conf)
	assert.NotEmpty(t, result)
	assert.Contains(t, result, "http://localhost:5000/api/private/mf-model-api/v1")
}

// TestGetModelApiUrlPrefix_URLStructure tests the structure of the generated URL
func TestGetModelApiUrlPrefix_URLStructure(t *testing.T) {
	conf := &cconf.ModelFactoryConf{
		ModelApiSvc: cconf.SvcConf{
			Protocol: "https",
			Host:     "api.example.com",
			Port:     443,
		},
	}

	result := getModelApiUrlPrefix(conf)

	// Check that the URL has the expected structure
	expectedPrefix := "https://api.example.com:443/api/private/mf-model-api/v1"
	assert.Equal(t, expectedPrefix, result)
}
