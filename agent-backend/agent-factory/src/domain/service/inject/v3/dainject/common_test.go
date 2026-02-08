package dainject

import (
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/cconf"
	"github.com/stretchr/testify/assert"
)

func TestGetModelApiUrlPrefix(t *testing.T) {
	t.Run("returns url prefix with http protocol", func(t *testing.T) {
		conf := &cconf.ModelFactoryConf{
			ModelApiSvc: cconf.SvcConf{
				Protocol: "http",
				Host:     "localhost",
				Port:     8080,
			},
		}

		result := getModelApiUrlPrefix(conf)

		assert.Contains(t, result, "http://localhost:8080/api/private/mf-model-api/v1")
	})

	t.Run("returns url prefix with https protocol", func(t *testing.T) {
		conf := &cconf.ModelFactoryConf{
			ModelApiSvc: cconf.SvcConf{
				Protocol: "https",
				Host:     "api.example.com",
				Port:     443,
			},
		}

		result := getModelApiUrlPrefix(conf)

		assert.Contains(t, result, "https://api.example.com:443/api/private/mf-model-api/v1")
	})

	t.Run("handles empty config", func(t *testing.T) {
		conf := &cconf.ModelFactoryConf{
			ModelApiSvc: cconf.SvcConf{
				Protocol: "",
				Host:     "",
				Port:     0,
			},
		}

		result := getModelApiUrlPrefix(conf)

		assert.Contains(t, result, "://:0/api/private/mf-model-api/v1")
	})
}
